import { defineStore } from 'pinia';
import { login, register, getMe, logout } from '@/api/auth';

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as null | { id: number; username: string; profile_name: string },
    loading: false,
    error: '',
  }),
  actions: {
    async fetchUser() {
      try {
        this.user = await getMe();
      } catch {
        this.user = null;
      }
    },
    async login(username: string, password: string) {
      await login(username, password);
      await this.fetchUser();
    },
    async register(username: string, profileName: string, password: string) {
      await register(username, profileName, password);
      await this.fetchUser();
    },
    async logout() {
      await logout();
      this.user = null;
    },
  },
});
