<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Daftar Pengguna Terdaftar</h1>

    <div v-if="isLoading" class="text-center py-10">
      <p class="text-gray-500">Memuat data pengguna...</p>
    </div>
    
    <div v-else-if="error" class="bg-red-100 text-red-700 p-4 rounded-md">
      {{ error }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="user in userList" :key="user.email" class="bg-white p-5 rounded-lg shadow-md flex flex-col items-center text-center">
        <img :src="getImageUrl(user.photo_url)" alt="Foto Profil" class="w-24 h-24 rounded-full object-cover mb-4 ring-4 ring-gray-200">
        <h2 class="text-lg font-bold text-gray-900">{{ user.name }}</h2>
        <p class="text-sm text-gray-600">{{ user.email }}</p>
        <span class="mt-2 px-3 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full uppercase">{{ user.role }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const userList = ref([]);
const isLoading = ref(true);
const error = ref(null);
const router = useRouter();

// URL dasar dari server backend kita
const API_BASE_URL = 'http://127.0.0.1:8000';

onMounted(async () => {
  const token = localStorage.getItem("token");

  // Jika tidak ada token, jangan lanjutkan dan arahkan ke login
  if (!token) {
    router.push('/');
    return;
  }

  try {
    // Gunakan VITE_API_BASE_URL jika ada, jika tidak gunakan string kosong
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/users`;
    const res = await fetch(apiUrl, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) {
      if (res.status === 401) {
        // Token tidak valid atau kedaluwarsa
        router.push('/');
        throw new Error("Sesi Anda telah berakhir. Silakan login kembali.");
      }
      const errData = await res.json();
      throw new Error(errData.detail || "Gagal mengambil data pengguna.");
    }
    
    userList.value = await res.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
});

// --- FUNGSI BARU UNTUK MENAMPILKAN GAMBAR ---
const getImageUrl = (photoUrl) => {
  // Jika tidak ada URL foto, tampilkan placeholder atau gambar default
  if (!photoUrl || photoUrl === "") {
    // Ganti dengan path ke gambar placeholder jika Anda punya
    return 'https://via.placeholder.com/150'; 
  }
  // Gabungkan URL backend dengan path relatif dari database
  return `${API_BASE_URL}${photoUrl}`;
};
</script>