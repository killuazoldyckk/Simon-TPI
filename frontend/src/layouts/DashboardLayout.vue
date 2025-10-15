<template>
  <div class="flex h-screen bg-gray-100">
    <Sidebar />

    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white shadow-md flex items-center justify-between px-6">
        <h1 class="text-2xl font-semibold text-blue-900">{{ $route.name }}</h1>
        <div class="flex items-center space-x-4">
          <span class="text-gray-700">Halo, {{ user.name }}!</span>
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
const user = ref({ name: 'Pengguna', photo_url: '' });

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  router.push('/');
};

// Ambil nama pengguna saat komponen dimuat
onMounted(async () => {
  const token = localStorage.getItem('token'); // Ambil token
  if (!token) {
    // Jika tidak ada token, jangan lanjutkan
    return;
  }
  
  try {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/profile`;
    const response = await fetch(apiUrl, {
      headers: {
        'Authorization': `Bearer ${token}` // <-- TAMBAHKAN HEADER INI
      }
    });
    if (response.ok) {
      user.value = await response.json();
    }
  } catch (error) {
    console.error('Gagal mengambil profil pengguna:', error);
  }
});
</script>