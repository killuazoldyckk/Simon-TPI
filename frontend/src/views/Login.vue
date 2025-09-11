<template>
  <div class="flex h-screen items-center justify-center bg-gray-100">
    <form @submit.prevent="login" class="bg-white p-6 rounded shadow w-80">
      <h1 class="text-xl mb-4">Login SIMON TPI</h1>
      <input v-model="email" type="email" placeholder="Email"
             class="border p-2 w-full mb-2" />
      <input v-model="password" type="password" placeholder="Password"
             class="border p-2 w-full mb-2" />
      <button class="bg-blue-600 text-white px-4 py-2 w-full rounded">Login</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const email = ref('')
const password = ref('')

async function login() {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.value, password: password.value })
  })
  if (!res.ok) {
    alert("Login gagal")
    return
  }
  const data = await res.json()
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('role', data.role)
  router.push('/dashboard')
}
</script>
