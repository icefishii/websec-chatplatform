<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/store/user';
import { useRouter } from 'vue-router';

const router = useRouter();
const userStore = useUserStore();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

async function handleLogin() {
  error.value = '';
  loading.value = true;
  try {
    await userStore.login(username.value, password.value);
    router.push('/');
  } catch (err: any) {
    error.value = err.detail || 'Login failed';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <label>Username</label>
      <input v-model="username" required /><br>

      <label>Password</label>
      <input v-model="password" type="password" required /><br>

      <button :disabled="loading">
        {{ loading ? "Logging in..." : "Login" }}
      </button>
    </form>

    <RouterLink to="/register">No account yet? Register</RouterLink>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style scoped>
.login-container { max-width: 400px; margin: 2rem auto; }
.error { color: red; }
</style>
