<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { tryCatch } from "@/api/utils";
import { login } from "@/api/auth";

const router = useRouter();

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  error.value = "";
  loading.value = true;

  const [, err] = await tryCatch(login(username.value, password.value));

  if (err) {
    // Handle error safely — your backend sends JSON with { detail }
    error.value = (err as Error).message || "Login failed";
  } else {
    // Successful login — redirect
    router.push("/");
  }

  loading.value = false;
}
</script>

<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <label>Username</label>
      <input v-model="username" required class="border rounded p-1 w-full mb-2" />

      <label>Password</label>
      <input v-model="password" type="password" required class="border rounded p-1 w-full" />

      <button
        :disabled="loading"
        class="px-3 py-1 border rounded bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
      >
        {{ loading ? "Logging in..." : "Login" }}
      </button>
    </form>

    <RouterLink to="/register" class="text-emerald-500 hover:underline block mt-4">
      No account yet? Register
    </RouterLink>

    <p v-if="error" class="error mt-2">{{ error }}</p>
  </div>
</template>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 4rem auto;
  display: flexbox;
  align-content: center;
}
.error {
  color: red;
}

button {
  margin-top: 1rem;
}
</style>
