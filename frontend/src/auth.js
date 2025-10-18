// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))
  const userRole = ref(localStorage.getItem('role'))
  const router = useRouter()

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userRole.value === 'admin')

  function setToken(newToken, role) {
    token.value = newToken
    userRole.value = role
    localStorage.setItem('token', newToken)
    localStorage.setItem('role', role)
  }

  function logout() {
    token.value = null
    userRole.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    router.push('/')
  }

  return { token, userRole, isLoggedIn, isAdmin, setToken, logout }
})