<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { tryCatch } from "@/api/utils";
import { register } from "@/api/auth";

const router = useRouter();

const username = ref("");
const profileName = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function handleRegister() {
  error.value = "";
  loading.value = true;

  const [, err] = await tryCatch(register(username.value, profileName.value, password.value));

  if (err) {
    error.value = (err as Error).message || "Registration failed";
  } else {
    router.push("/");
  }

  loading.value = false;
}
</script>

<template>
  <div class="register-container">
    <h1>Register</h1>
    <form @submit.prevent="handleRegister">
      <label>Username</label>
      <input v-model="username" required class="border rounded p-1 w-full mb-2" />

      <label>Profile Name</label>
      <input v-model="profileName" required class="border rounded p-1 w-full mb-2" />

      <label>Password</label>
      <input v-model="password" type="password" required class="border rounded p-1 w-full mb-4" />

      <button
        :disabled="loading"
        class="px-3 py-1 border rounded bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
      >
        {{ loading ? "Registering..." : "Register" }}
      </button>
    </form>

    <RouterLink to="/login" class="text-emerald-500 hover:underline block mt-4">
      Already have an account? Login
    </RouterLink>

    <p v-if="error" class="error mt-2">{{ error }}</p>
  </div>
</template>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 4rem auto;
}
button {
  margin-top: 1rem;
}
.error {
  color: red;
}
</style>
