<template>
  <div class="flex h-screen bg-gray-100">
    <Sidebar />

    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white shadow-md flex items-center justify-between px-6">
        <h1 class="text-2xl font-semibold text-blue-900">{{ $route.name }}</h1>
        <div class="flex items-center space-x-4">
          <span class="text-gray-700">Halo, {{ userName }}!</span>
          <button @click="logout" class="bg-red-500 text-white px-3 py-1 rounded text-sm">
            Logout
          </button>
        </div>
      </header>

      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Sidebar from '../components/Sidebar.vue';

const router = useRouter();
const userName = ref('Pengguna'); // Nilai default

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  router.push('/');
};

// Ambil nama pengguna saat komponen dimuat
onMounted(async () => {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch("/api/profile", {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (res.ok) {
      const profile = await res.json();
      userName.value = profile.name; // Perbarui nama pengguna
    }
  } catch (err) {
    console.error("Gagal mengambil profil untuk layout:", err);
  }
});
</script>