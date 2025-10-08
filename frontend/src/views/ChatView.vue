<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from "vue";
import { useRoute } from "vue-router";
import { getConversationMessages, sendMessage } from "@/api/messages";
import { tryCatch } from "@/api/utils";
import Bubble from "@/components/Bubble.vue";
import { useAuth } from "@/api/useAuth";

/* Replace the generic Message type with a local ChatMessage type that explicitly
   allows null for sender_id/recipient_id to avoid the TS error when creating
   transient messages with null sender_id. */
interface ChatMessage {
  id?: string;
  sender_id?: string | null;
  recipient_id?: string | null;
  content: string;
  created_at?: string;
}

const route = useRoute();
const { currentUser } = useAuth(); // observe auth
const userId = ref<string | null>((route.params.id as string) || null);
const messages = ref<ChatMessage[]>([]);
const newMessage = ref("");
const isLoading = ref(false);
const isError = ref(false);
const listRef = ref<HTMLElement | null>(null);

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

watch(
  () => route.params.id,
  (v) => {
    userId.value = v as string;
    loadMessages();
  },
  { immediate: true },
);

watch(
  () => currentUser.value,
  (val, oldVal) => {
    console.log(val, oldVal);
    if (userId.value) loadMessages();
  },
);

onMounted(() => {
  loadMessages();
});

async function sendHandler() {
  if (!userId.value || !newMessage.value.trim()) return;
  try {
    const sent = await sendMessage(userId.value, newMessage.value.trim());
    const item: ChatMessage =
      typeof sent === "object"
        ? (sent as ChatMessage)
        : {
            content: newMessage.value.trim(),
            sender_id: null,
            created_at: new Date().toISOString(),
          };
    messages.value.push(item);
    newMessage.value = "";
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
  <main class="flex-1 min-h-[calc(100vh-4rem)] flex items-stretch">
    <div
      class="w-full max-w-4xl mx-auto px-4 py-6 flex flex-col"
      style="min-height: calc(100vh - 6rem)"
    >
      <div class="flex-1 overflow-auto mb-4" ref="listRef">
        <div v-if="isLoading" class="flex items-center justify-center py-6">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-400"></div>
        </div>

        <div v-else-if="isError" class="text-red-400 text-center py-4">Failed to load messages</div>

        <div v-else class="px-2">
          <Bubble v-for="msg in messages" :key="msg.id || msg.created_at" :message="msg" />
        </div>
      </div>

      <form @submit.prevent="sendHandler" class="flex gap-2 items-center">
        <input
          v-model="newMessage"
          type="text"
          placeholder="Write a message..."
          class="flex-1 px-3 py-2 rounded-md bg-emerald-900 text-emerald-100 focus:outline-none"
        />
        <button type="submit" class="px-4 py-2 bg-emerald-400 text-emerald-950 rounded-md">
          Send
        </button>
      </form>
    </div>
  </main>
</template>

<style scoped>
/* keep chat layout comfortable */
</style>
