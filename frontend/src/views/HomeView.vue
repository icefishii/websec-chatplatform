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
  <div class="h-full w-full flex items-center justify-center px-4">
    <div class="w-full max-w-3xl text-center">
      <div v-if="isLoading" class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400"></div>
      </div>

      <template v-else>
        <h1 class="text-2xl font-semibold mb-4">Welcome to the Chat Platform</h1>

        <div v-if="isAuthenticated">
          <p class="text-lg">
            Welcome <span class="font-medium">{{ currentUser?.username }}</span> — pick a
            conversation on the left to start chatting.
          </p>
        </div>

        <div v-else>
          <p class="mt-4 text-lg">Please login to continue</p>
        </div>
      </template>
    </div>
  </div>
</template>
