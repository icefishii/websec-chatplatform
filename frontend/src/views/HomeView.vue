<script setup lang="ts">
import { useAuth } from "@/api/useAuth";
import { watch, ref } from "vue";

const { currentUser } = useAuth();
const isAuthenticated = ref(false);
const isLoading = ref(true);

watch(
  () => currentUser.value,
  (newValue) => {
    isAuthenticated.value = !!newValue;
    isLoading.value = false;
  },
  { immediate: true },
);
</script>

<template>
  <!-- App.vue already offsets content under the navbar (mt-16). remove duplicate margin here -->
  <main class="flex-1 min-h-[calc(100vh-4rem)] flex items-center justify-center">
    <div class="w-full max-w-3xl px-6 text-center">
      <div v-if="isLoading" class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400"></div>
      </div>

      <template v-else>
        <h1 class="text-2xl font-semibold mb-4">Welcome to the Chat Platform</h1>

        <div v-if="isAuthenticated" class="text-left">
          <p class="text-lg">Welcome <span class="font-medium">{{ currentUser?.username }}</span> — pick a conversation on the left to start chatting.</p>
        </div>

        <div v-else class="text-center">
          <p class="mt-4 text-lg">Please login to continue</p>
        </div>
      </template>
    </div>
  </main>
</template>
