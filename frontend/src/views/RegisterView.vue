<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/store/user";
import { useRouter } from "vue-router";

const router = useRouter();
const userStore = useUserStore();

const username = ref("");
const profileName = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function handleRegister() {
  error.value = "";
  loading.value = true;
  try {
    await userStore.register(username.value, profileName.value, password.value);
    router.push("/");
  } catch (err: unknown) {
    error.value = (err as Error).message || "Registration failed";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="register-container">
    <h1>Register</h1>
    <form @submit.prevent="handleRegister">
      <label>Username </label>
      <input v-model="username" required /><br />
      <label>Profile Name </label>
      <input v-model="profileName" required /><br />
      <label>Password </label>
      <input v-model="password" type="password" required /><br />

      <button :disabled="loading">
        {{ loading ? "Registering..." : "Register" }}
      </button>
    </form>

    <RouterLink to="/login">Already have an account? Login</RouterLink>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 2rem auto;
}
.error {
  color: red;
}
</style>
