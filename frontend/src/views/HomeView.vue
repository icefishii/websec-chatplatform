<script setup lang="ts">
import { useAuth } from "@/api/useAuth";
import { onMounted, watch, ref } from "vue";

const { currentUser, fetchCurrentUser } = useAuth();

// Reactive reference to track authentication state
const isAuthenticated = ref(false);

// Update authentication state when currentUser changes
watch(
  () => currentUser,
  (newValue) => {
    isAuthenticated.value = !!newValue;
  },
  { immediate: true },
);

onMounted(async () => {
  await fetchCurrentUser();
});
</script>

<template>
  <main class="flex min-h-screen flex-col items-center justify-between">
    <div v-if="isAuthenticated">
      <!-- Authenticated content -->
      <h1>Welcome {{ currentUser?.username }}!</h1>
      <!-- Your authenticated view content -->
    </div>
    <div v-else>
      <!-- Non-authenticated content -->
      <h1>Welcome to the Chat Platform</h1>
      <p>Please login to continue</p>
    </div>
  </main>
</template>
