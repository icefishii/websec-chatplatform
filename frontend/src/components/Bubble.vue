<script setup lang="ts">
defineOptions({ name: "ChatBubble" });

import { computed } from "vue";
import { useAuth } from "@/api/useAuth";

interface ChatMessage {
  id?: string;
  sender_id?: string | null;
  recipient_id?: string | null;
  content: string;
  created_at?: string;
}

const props = defineProps<{
  message: ChatMessage;
}>();

const { currentUser } = useAuth();

const isMine = computed(() => {
  if (!currentUser.value) return false;
  return props.message.sender_id === currentUser.value.id;
});

const formattedTime = computed(() => {
  if (!props.message.created_at) return "";
  try {
    return new Date(props.message.created_at).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
});
</script>

<template>
  <div :class="['flex items-end gap-3', isMine ? 'justify-end' : 'justify-start']">
    <div
      v-if="!isMine"
      class="flex h-6 w-6 items-center justify-center text-emerald-400"
    >
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path
          d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z"
        />
      </svg>
    </div>

    <div
      :class="[
        'max-w-[70%] break-words rounded-lg px-4 py-3 shadow',
        isMine
          ? 'rounded-br-none bg-emerald-400 text-emerald-950'
          : 'rounded-bl-none bg-emerald-900 text-emerald-100'
      ]"
    >
      <div class="whitespace-pre-wrap text-sm">{{ message.content }}</div>
      <div class="mt-1 text-right text-xs opacity-70">{{ formattedTime }}</div>
    </div>
  </div>
</template>

<style scoped>
/* keep bubbles compact */
</style>