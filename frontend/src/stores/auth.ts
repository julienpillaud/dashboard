import { defineStore } from 'pinia'
import api from '@/services/api'

export interface User {
  id: number
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null') as User | null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.user,
  },
  actions: {
    async login(email: string, password: string) {
      const body = new URLSearchParams({ username: email, password })
      const { data } = await api.post<User>('/auth/login', body)
      this.setUser(data)
    },
    async logout() {
      await api.post('/auth/logout').catch(() => {})
      this.clear()
    },
    setUser(user: User) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    clear() {
      this.user = null
      localStorage.removeItem('user')
    },
  },
})
