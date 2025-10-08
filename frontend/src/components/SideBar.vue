<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { Fa6User } from "vue-icons-plus/fa6";
import { useAuth } from "@/api/useAuth";
import { tryCatch } from "@/api/utils";
import { getConversations, sendMessage, findProfilesByName } from "@/api/messages";
import { useRouter, useRoute } from "vue-router";

interface Conversation {
  id: string;
  profile_name: string;
  last_message?: string;
  last_message_time?: string;
}

interface User {
  id: string;
  username: string;
  lastMessage?: string;
  isOnline?: boolean;
}

const { currentUser } = useAuth();
const users = ref<User[]>([]);
const isLoading = ref(false);
const isError = ref(false);

const searchTerm = ref("");
const showNewConvo = ref(false);
const newConvoName = ref("");
const newConvoMessage = ref("");
const newConvoError = ref<string | null>(null);

const router = useRouter();
const route = useRoute();

const selectedConversationId = computed(() => (route.params.id as string) || null);

const fetchConversations = async () => {
  isLoading.value = true;
  isError.value = false;
  const [convos, error] = await tryCatch(getConversations());
  if (error) {
    console.error(error);
    users.value = [];
    isError.value = true;
    isLoading.value = false;
    return;
  }
  if (Array.isArray(convos)) {
    users.value = convos.map((c: Conversation) => ({
      id: c.id,
      username: c.profile_name,
      lastMessage: c.last_message || "",
    }));
  } else {
    users.value = [];
  }
  isLoading.value = false;
};

watch(
  () => currentUser.value,
  (val) => {
    if (val) fetchConversations();
    else {
      users.value = [];
      isError.value = false;
      isLoading.value = false;
    }
  },
  { immediate: true },
);

const filteredUsers = computed(() => {
  const q = searchTerm.value.trim().toLowerCase();
  if (!q) return users.value;
  return users.value.filter(
    (u) => u.username.toLowerCase().includes(q) || (u.lastMessage ?? "").toLowerCase().includes(q),
  );
});

function openChat(id: string) {
  // clear search so list stays visible after navigation
  searchTerm.value = "";
  router.push({ name: "chat", params: { id } }).catch(() => {
    router.push(`/chat/${id}`).catch(() => {});
  });
}

async function startNewConvoByName(name: string, firstMessage?: string) {
  newConvoError.value = null;
  if (!name.trim()) {
    newConvoError.value = "Please enter a profile name";
    return;
  }
  isLoading.value = true;
  // try to resolve profile by name from backend (robust: returns [] if backend doesn't have)
  const [profiles, pErr] = await tryCatch(findProfilesByName(name.trim()));
  if (pErr) {
    console.error(pErr);
    newConvoError.value = "Failed to search users";
    isLoading.value = false;
    return;
  }
  if (!Array.isArray(profiles) || profiles.length === 0) {
    newConvoError.value = `No user found with name "${name.trim()}"`;
    isLoading.value = false;
    return;
  }
  // pick first match
  const target = profiles[0];
  try {
    if (firstMessage && firstMessage.trim()) {
      // sending a message will effectively create the conversation server-side
      await sendMessage(target.id, firstMessage.trim());
    }
    // optimistic UI: insert into users list and navigate
    const exists = users.value.find((u) => u.id === target.id);
    if (!exists) {
      users.value.unshift({
        id: target.id,
        username: target.profile_name ?? target.username ?? name.trim(),
        lastMessage: firstMessage?.trim() || "",
      });
    }
    // clear search and close modal
    searchTerm.value = "";
    showNewConvo.value = false;
    newConvoName.value = "";
    newConvoMessage.value = "";
    newConvoError.value = null;
    openChat(target.id);
  } catch (e) {
    console.error(e);
    newConvoError.value = "Failed to start conversation";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <aside
    v-if="currentUser"
    class="fixed left-0 top-16 h-[calc(100vh-4rem)] w-52 bg-emerald-950 p-3 overflow-y-auto z-40"
  >
    <div class="space-y-3">
      <input
        v-model="searchTerm"
        type="text"
        placeholder="Search conversations..."
        class="w-full px-2 py-1 bg-emerald-900 text-emerald-100 rounded-md placeholder-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-400"
      />

      <div class="mt-2">
        <div v-if="isLoading" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-400"></div>
        </div>

        <div v-else-if="isError" class="text-red-400 text-center py-4">
          Failed to load conversations
        </div>

        <div v-else>
          <div v-if="filteredUsers.length">
            <div
              v-for="user in filteredUsers"
              :key="user.id"
              @click="openChat(user.id)"
              :class="[
                'flex items-start gap-3 px-2 py-2 rounded-md hover:bg-emerald-900 cursor-pointer transition-colors',
                selectedConversationId === user.id ? 'bg-emerald-800 ring-1 ring-emerald-600' : ''
              ]"
            >
              <div class="relative mt-1">
                <Fa6User class="text-emerald-400 w-5 h-5" />
              </div>

              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-2">
                  <div :class="['font-semibold text-sm truncate', selectedConversationId === user.id ? 'text-emerald-100' : 'text-emerald-100']">
                    {{ user.username }}
                  </div>
                </div>
                <div class="text-emerald-200 text-xs truncate mt-0.5">
                  {{ user.lastMessage }}
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-emerald-400 text-sm text-center py-4">
            No conversations match.
            <div class="mt-2">
              <button
                v-if="searchTerm.trim() && !showNewConvo"
                @click="
                  () => {
                    showNewConvo = true;
                    newConvoName = searchTerm;
                  }
                "
                class="px-3 py-1 mt-2 bg-emerald-400 text-emerald-950 rounded-md"
              >
                Start conversation with "{{ searchTerm }}"
              </button>
            </div>
          </div>

          <!-- New conversation form -->
          <div v-if="showNewConvo" class="mt-3 p-2 bg-emerald-900 rounded-md">
            <label class="text-emerald-100 text-xs">Profile name</label>
            <input
              v-model="newConvoName"
              type="text"
              class="w-full mt-1 px-2 py-1 rounded bg-emerald-800 text-emerald-100"
            />

            <label class="text-emerald-100 text-xs mt-2 block">First message (optional)</label>
            <input
              v-model="newConvoMessage"
              type="text"
              class="w-full mt-1 px-2 py-1 rounded bg-emerald-800 text-emerald-100"
            />

            <div class="flex gap-2 mt-2">
              <button
                @click="() => startNewConvoByName(newConvoName, newConvoMessage)"
                class="px-3 py-1 bg-emerald-400 text-emerald-950 rounded-md"
              >
                Start
              </button>
              <button
                @click="
                  () => {
                    showNewConvo = false;
                    newConvoError = null;
                  }
                "
                class="px-3 py-1 bg-emerald-700 text-emerald-200 rounded-md"
              >
                Cancel
              </button>
            </div>

            <div v-if="newConvoError" class="text-red-400 text-sm mt-2">
              {{ newConvoError }}
            </div>
          </div>

          <div v-if="users.length === 0" class="text-emerald-400 text-sm text-center py-4">
            No conversations yet
          </div>
        </div>
      </div>
    </div>
  </aside>

  <!-- New convo modal (full-screen) -->
  <div
    v-if="showNewConvo"
    class="fixed inset-0 z-60 flex items-center justify-center"
    role="dialog"
    aria-modal="true"
  >
    <div class="absolute inset-0 bg-black/60" @click="() => { showNewConvo = false; searchTerm = '' }"></div>
    <div class="relative w-full max-w-md p-4 bg-emerald-950 rounded-md shadow-lg">
      <h3 class="text-emerald-100 font-semibold mb-2">Start conversation</h3>
      <label class="text-emerald-300 text-xs">Profile name</label>
      <input v-model="newConvoName" type="text" class="w-full mt-1 px-2 py-1 rounded bg-emerald-800 text-emerald-100" />

      <label class="text-emerald-300 text-xs mt-3 block">First message (optional)</label>
      <input v-model="newConvoMessage" type="text" class="w-full mt-1 px-2 py-1 rounded bg-emerald-800 text-emerald-100" />

      <div class="flex gap-2 justify-end mt-4">
        <button
          @click="() => { showNewConvo = false; searchTerm = '' }"
          class="px-3 py-1 bg-emerald-700 text-emerald-200 rounded-md"
        >
          Cancel
        </button>
        <button
          @click="() => startNewConvoByName(newConvoName, newConvoMessage)"
          class="px-3 py-1 bg-emerald-400 text-emerald-950 rounded-md"
        >
          Start
        </button>
      </div>

      <div v-if="newConvoError" class="text-red-400 text-sm mt-2">
        {{ newConvoError }}
      </div>
    </div>
  </div>
</template>

<style scoped>
aside {
  border-right: 1px solid rgb(16 185 129 / 0.06);
}
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #047857;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #059669;
}
</style>
