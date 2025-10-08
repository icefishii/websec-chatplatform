<script setup lang="ts">
import { useAuth } from "@/api/useAuth";
import { onMounted, watch } from "vue";
import { useRouter } from "vue-router";

const { currentUser, fetchCurrentUser, logout } = useAuth();
const router = useRouter();

async function logoutWrapper() {
  await logout();
  await router.push("/");
  await fetchCurrentUser();
}

// Watch for route changes to refresh user state
watch(() => router.currentRoute.value.path, async () => {
  await fetchCurrentUser();
});

onMounted(fetchCurrentUser);
</script>

<template>
  <nav
    class="fixed top-0 left-0 w-full flex justify-between items-center p-4 shadow-md bg-emerald-950"
  >
    <RouterLink to="/" class="flex items-center gap-2 rounded-md">
      <img alt="Vue logo" src="@/assets/logo.svg" width="32" height="32" />
    </RouterLink>

    <div class="flex gap-4">
      <template v-if="currentUser">
        <RouterLink 
          to="/" 
          custom 
          v-slot="{ navigate }"
        >
          <a 
            @click="async (e) => { 
              e.preventDefault(); 
              await logoutWrapper(); 
              navigate(); 
            }" 
            class="text-emerald-400 px-3 py-1 border rounded transition hover:bg-emerald-900"
          >
            Logout
          </a>
        </RouterLink>
        <span class="px-3 py-1 rounded transition">
          {{ currentUser.username }}
        </span>
      </template>

      <template v-else>
        <RouterLink 
          to="/login" 
          class="text-emerald-400 px-3 py-1 border rounded transition hover:bg-emerald-900"
        >
          Login
        </RouterLink>
        <RouterLink 
          to="/register" 
          class="text-emerald-400 px-3 py-1 border rounded transition hover:bg-emerald-900"
        >
          Register
        </RouterLink>
      </template>
    </div>
  </nav>
</template>

<style scoped>
span {
  color: #00bd7e;
}

a {
  text-decoration: none;
}

.router-link-active {
  color: #00bd7e;
}
</style>
