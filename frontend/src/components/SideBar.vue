<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { Fa6User } from "vue-icons-plus/fa6";
import { useAuth } from "@/api/useAuth";
import { tryCatch, type Conversation, type SearchResult, type User } from "@/api/utils";
import { getConversations, findProfilesByName } from "@/api/messages";
import { useRouter, useRoute } from "vue-router";

// Define window interface extension
declare global {
  interface Window {
    __updateSidebarMessage?: (userId: string, message: string, profileName?: string) => void;
  }
}

const { currentUser } = useAuth();
const users = ref<User[]>([]);
const isLoading = ref(false);
const isError = ref(false);

const searchTerm = ref("");
const searchResults = ref<SearchResult[]>([]);
const isSearching = ref(false);
const showSearchResults = ref(false);
let searchTimeout: ReturnType<typeof setTimeout> | null = null;

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

// Expose method to update last message from outside
const updateLastMessage = (userId: string, message: string, profileName?: string) => {
  const existingUser = users.value.find((u) => u.id === userId);
  if (existingUser) {
    // Update existing conversation
    existingUser.lastMessage = message;
    // Move to top of list
    users.value = [existingUser, ...users.value.filter((u) => u.id !== userId)];
  } else if (profileName) {
    // Add new conversation at top
    users.value.unshift({
      id: userId,
      username: profileName,
      lastMessage: message,
    });
  }
};

// Make it available globally via window for ChatView to access
if (typeof window !== "undefined") {
  window.__updateSidebarMessage = updateLastMessage;
}

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

// Debounced search function
watch(searchTerm, (newVal) => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }

  const trimmed = newVal.trim();

  if (!trimmed) {
    showSearchResults.value = false;
    searchResults.value = [];
    return;
  }

  searchTimeout = setTimeout(async () => {
    if (trimmed.length > 0) {
      isSearching.value = true;
      const [results, error] = await tryCatch(findProfilesByName(trimmed, 20));

      if (error) {
        console.error("Search error:", error);
        searchResults.value = [];
      } else {
        searchResults.value = Array.isArray(results) ? results : [];
      }

      showSearchResults.value = true;
      isSearching.value = false;
    }
  }, 500);
});

function openChat(id: string) {
  searchTerm.value = "";
  showSearchResults.value = false;
  searchResults.value = [];
  router.push({ name: "chat", params: { id } }).catch(() => {
    router.push(`/chat/${id}`).catch(() => {});
  });
}

async function startChatWithUser(userId: string, profileName: string) {
  const existingConvo = users.value.find((u) => u.id === userId);

  if (existingConvo) {
    openChat(userId);
  } else {
    users.value.unshift({
      id: userId,
      username: profileName,
      lastMessage: "",
    });
    openChat(userId);
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
        <!-- Search results view -->
        <div v-if="showSearchResults">
          <div class="text-emerald-300 text-xs font-semibold mb-2 px-2">Search Results</div>

          <div v-if="isSearching" class="flex justify-center py-4">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-400"></div>
          </div>

          <div
            v-else-if="searchResults.length === 0"
            class="text-emerald-400 text-sm text-center py-4"
          >
            No users found matching "{{ searchTerm }}"
          </div>

          <div v-else class="space-y-1">
            <div
              v-for="result in searchResults"
              :key="result.id"
              @click="startChatWithUser(result.id, result.profile_name)"
              class="flex items-start gap-3 px-2 py-2 rounded-md hover:bg-emerald-900 cursor-pointer transition-colors"
            >
              <div class="relative mt-1">
                <Fa6User class="text-emerald-400 w-5 h-5" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-emerald-100 font-semibold text-sm truncate">
                  {{ result.profile_name }}
                </div>
                <div class="text-emerald-400 text-xs">Click to start chat</div>
              </div>
            </div>
          </div>

          <button
            @click="
              () => {
                searchTerm = '';
                showSearchResults = false;
                searchResults = [];
              }
            "
            class="w-full mt-3 px-3 py-1 bg-emerald-800 text-emerald-200 rounded-md text-sm hover:bg-emerald-700"
          >
            Back to conversations
          </button>
        </div>

        <!-- Conversations view -->
        <div v-else>
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
                  selectedConversationId === user.id
                    ? 'bg-emerald-800 ring-1 ring-emerald-600'
                    : '',
                ]"
              >
                <div class="relative mt-1">
                  <Fa6User class="text-emerald-400 w-5 h-5" />
                </div>

                <div class="min-w-0 flex-1">
                  <div class="flex items-center justify-between gap-2">
                    <div
                      :class="[
                        'font-semibold text-sm truncate',
                        selectedConversationId === user.id
                          ? 'text-emerald-100'
                          : 'text-emerald-100',
                      ]"
                    >
                      {{ user.username }}
                    </div>
                  </div>
                  <div class="text-emerald-200 text-xs truncate mt-0.5">
                    {{ user.lastMessage }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="users.length === 0" class="text-emerald-400 text-sm text-center py-4">
              No conversations yet
            </div>

            <div v-else class="text-emerald-400 text-sm text-center py-4">
              No conversations match your filter
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
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
