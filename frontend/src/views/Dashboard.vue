<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold">Dashboard SIMON TPI</h1>
    <p class="mt-2">Halo, {{ user?.email }} (role: {{ user?.role }})</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const user = ref(null)
onMounted(async () => {
  const res = await fetch('/api/users/me', {
    headers: { Authorization: "Bearer " + localStorage.getItem('token') }
  })
  user.value = await res.json()
})
</script>
