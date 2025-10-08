<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from "vue";
import { useRoute } from "vue-router";
import { getConversationMessages, sendMessage } from "@/api/messages";
import { tryCatch, type ChatMessage } from "@/api/utils";
import Bubble from "@/components/Bubble.vue";
import { useAuth } from "@/api/useAuth";

// Define window interface extension
declare global {
  interface Window {
    __updateSidebarMessage?: (userId: string, message: string, profileName?: string) => void;
  }
}

const route = useRoute();
const { currentUser } = useAuth();
const userId = ref<string | null>((route.params.id as string) || null);
const messages = ref<ChatMessage[]>([]);
const newMessage = ref("");
const isLoading = ref(false);
const isError = ref(false);
const listRef = ref<HTMLElement | null>(null);
const otherUserProfile = ref<string>("");

async function loadMessages() {
  if (!userId.value) return;
  isLoading.value = true;
  isError.value = false;
  const [data, err] = await tryCatch(getConversationMessages(userId.value!, 100, 0));
  if (err) {
    console.error(err);
    isError.value = true;
    messages.value = [];
  } else {
    messages.value = Array.isArray(data) ? (data as ChatMessage[]) : [];
    await nextTick();
    scrollToBottom();
  }
  isLoading.value = false;
}

// Fetch other user's profile name for sidebar updates
async function fetchOtherUserProfile() {
  if (!userId.value) return;
  try {
    const res = await fetch(`/api/v1/users/${userId.value}`, { credentials: "include" });
    if (res.ok) {
      const data = await res.json();
      otherUserProfile.value = data.profile_name || data.username || "";
    }
  } catch (e) {
    console.warn("Could not fetch user profile:", e);
  }
}

watch(
  () => route.params.id,
  (v) => {
    userId.value = v as string;
    loadMessages();
    fetchOtherUserProfile();
  },
  { immediate: true },
);

watch(
  () => currentUser.value,
  () => {
    if (userId.value) {
      loadMessages();
      fetchOtherUserProfile();
    }
  },
);

onMounted(() => {
  loadMessages();
  fetchOtherUserProfile();
});

async function sendHandler() {
  if (!userId.value || !newMessage.value.trim()) return;
  const messageContent = newMessage.value.trim();

  try {
    const sent = await sendMessage(userId.value, messageContent);
    const item: ChatMessage =
      typeof sent === "object"
        ? (sent as ChatMessage)
        : {
            content: messageContent,
            sender_id: currentUser.value?.id || null,
            created_at: new Date().toISOString(),
          };
    messages.value.push(item);
    newMessage.value = "";

    // Update sidebar with latest message
    if (typeof window !== "undefined" && window.__updateSidebarMessage) {
      window.__updateSidebarMessage(userId.value, messageContent, otherUserProfile.value);
    }

    await nextTick();
    scrollToBottom();
  } catch (e) {
    console.error("send error", e);
  }
}

function scrollToBottom() {
  if (!listRef.value) return;
  listRef.value.scrollTop = listRef.value.scrollHeight;
}
</script>

<template>
  <div class="h-full w-full flex justify-center px-4 py-4">
    <div class="w-full max-w-4xl flex flex-col h-full gap-4">
      <!-- Messages container -->
      <div ref="listRef" class="flex-1 overflow-y-auto space-y-3 px-2">
        <div v-if="isLoading" class="flex items-center justify-center py-8">
          <div class="h-6 w-6 animate-spin rounded-full border-b-2 border-emerald-400"></div>
        </div>

        <div v-else-if="isError" class="py-6 text-center text-red-400">Failed to load messages</div>

        <template v-else>
          <Bubble v-for="msg in messages" :key="msg.id || msg.created_at" :message="msg" />
          <div v-if="messages.length === 0" class="py-6 text-center text-emerald-200">
            No messages yet. Say hi!
          </div>
        </template>
      </div>

      <!-- Message input - always at bottom -->
      <form
        @submit.prevent="sendHandler"
        class="flex gap-3 rounded-lg border border-emerald-800 bg-emerald-950/80 px-4 py-3 flex-shrink-0"
      >
        <input
          v-model="newMessage"
          type="text"
          placeholder="Write a message..."
          class="flex-1 rounded-md bg-emerald-900 px-4 py-2 text-emerald-100 focus:outline-none focus:ring-2 focus:ring-emerald-400"
        />
        <button
          type="submit"
          class="rounded-md bg-emerald-400 px-5 py-2 text-emerald-950 font-medium transition hover:bg-emerald-300 flex-shrink-0"
        >
          Send
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* keep chat layout comfortable */
</style>
