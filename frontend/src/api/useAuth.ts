import { ref } from "vue";
import { getMe, logout as apiLogout } from "@/api/auth";
import { tryCatch } from "@/api/utils";

const currentUser = ref<{ id: string; username: string } | null>(null);

export function useAuth() {
  async function fetchCurrentUser() {
    const [user, error] = await tryCatch(getMe());
    if (error) console.error(error.message);
    else if (user) currentUser.value = user;
  }

  async function logout() {
    await apiLogout();
    currentUser.value = null;
  }

  return {
    currentUser,
    fetchCurrentUser,
    logout,
  };
}
