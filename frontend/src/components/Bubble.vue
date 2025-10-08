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
  <div :class="['flex items-end gap-2 my-2', isMine ? 'justify-end' : 'justify-start']">
    <div v-if="!isMine" class="text-emerald-400 w-6 h-6 flex items-center justify-center">
      <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z"/>
      </svg>
    </div>

    <div :class="['max-w-[70%] break-words p-3 rounded-lg', isMine ? 'bg-emerald-400 text-emerald-950 rounded-br-none' : 'bg-emerald-900 text-emerald-100 rounded-bl-none']">
      <div class="text-sm whitespace-pre-wrap">{{ message.content }}</div>
      <div class="text-xs mt-1 opacity-70 text-right">{{ formattedTime }}</div>
    </div>

    <div v-if="isMine" class="text-emerald-400 w-6 h-6 flex items-center justify-center" aria-hidden="true"></div>
  </div>
</template>

<style scoped>
/* keep bubbles compact */
</style>