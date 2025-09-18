<template>
  <div class="flex h-screen bg-gray-100">
    <Sidebar />

    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white shadow-md flex items-center justify-between px-6">
        <h1 class="text-2xl font-semibold text-blue-900">{{ $route.name }}</h1>
        <div class="flex items-center space-x-4">
          <span class="text-gray-700 capitalize">Halo, {{ userRole }}!</span>
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
import { useRouter } from 'vue-router';
import Sidebar from '../components/Sidebar.vue';
// --- Impor ref dan onMounted ---
import { ref, onMounted } from 'vue';

const router = useRouter();
// --- Buat ref untuk role ---
const userRole = ref('Pengguna');

onMounted(() => {
  // Ambil role dari localStorage saat komponen dimuat
  const role = localStorage.getItem('role');
  if (role) {
    userRole.value = role;
  }
});

const logout = () => {
  localStorage.removeItem('token');
  // --- Hapus 'role' juga saat logout ---
  localStorage.removeItem('role'); 
  router.push('/');
};
</script>