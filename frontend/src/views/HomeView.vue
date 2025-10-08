<script setup lang="ts">
import { onMounted } from 'vue';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();

onMounted(() => {
  userStore.fetchUser();
});
</script>

<template>
  <div class="home">
    <h1>Welcome</h1>
    <div v-if="userStore.user">
      <p>Logged in as: <b>{{ userStore.user.profile_name }}</b></p>
      <button @click="userStore.logout()">Logout</button>
    </div>
    <div v-else>
      <RouterLink to="/login">Login</RouterLink>
      <RouterLink to="/register">Register</RouterLink>
    </div>
  </div>
</template>
