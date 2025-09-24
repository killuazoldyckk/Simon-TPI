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

onMounted(async () => {
  const token = localStorage.getItem("token");

  try {
    const res = await fetch("/api/users", {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) {
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

const getImageUrl = (photoUrl) => {
  if (!photoUrl) return '';
  if (photoUrl.startsWith('user_images/')) {
    return `/${photoUrl}`;
  } else {
    return new URL(`../assets/${photoUrl}`, import.meta.url).href;
  }
};
</script>