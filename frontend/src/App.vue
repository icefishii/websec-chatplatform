<script setup lang="ts">
import { onMounted } from "vue";
import { useAuth } from "@/api/useAuth";
import NavBar from "@/components/NavBar.vue";
import SideBar from "@/components/SideBar.vue";

const { fetchCurrentUser } = useAuth();

onMounted(() => {
  fetchCurrentUser();
});
</script>

<template>
  <div class="min-h-screen bg-[#242424] text-emerald-100">
    <NavBar />
    <SideBar />
    <main class="fixed left-52 right-0 top-16 bottom-0 overflow-hidden">
      <RouterView />
    </main>
  </div>
</template>
