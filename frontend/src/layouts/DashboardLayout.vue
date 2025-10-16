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
import { apiFetch } from '@/'; // <-- 1. Pastikan apiFetch diimpor
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
  // Anda bisa menyimpan pengecekan token di sini untuk menghindari panggilan API yang tidak perlu
  if (!localStorage.getItem('token')) {
    return;
  }
  
  try {
    // 2. Ganti fetch dengan apiFetch. Tidak perlu lagi mengatur header manual.
    const response = await apiFetch("/api/profile");
    
    if (response.ok) {
      user.value = await response.json();
    } else {
      // apiFetch sudah menangani redirect 401, baris ini hanya untuk logging jika ada error lain
      console.error('Gagal mengambil profil pengguna.');
    }
  } catch (error) {
    // Error (termasuk pesan "Sesi Anda telah berakhir") akan ditangkap di sini
    console.error(error.message);
  }
});
</script>