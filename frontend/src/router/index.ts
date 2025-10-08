// src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import ChatView from "@/views/ChatView.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/chat/:id", name: "chat", component: ChatView, props: true },
  { path: "/login", name: "login", component: LoginView },
  { path: "/register", name: "register", component: RegisterView },
];

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
