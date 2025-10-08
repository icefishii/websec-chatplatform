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
  <div>
    <NavBar />
    <SideBar />
    <main
      class="flex-1 ml-52 min-h-[calc(100vh-4rem)] flex items-center justify-center relative z-0"
    >
      <RouterView />
    </main>
  </div>
</template>
