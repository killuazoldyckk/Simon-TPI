<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Daftar Umpan Balik Pengguna</h1>

    <div v-if="isLoading" class="text-center py-10">
      <p class="text-gray-500">Memuat data...</p>
    </div>
    
    <div v-else-if="error" class="bg-red-100 text-red-700 p-4 rounded-md">
      {{ error }}
    </div>

    <div v-else-if="feedbackList.length > 0" class="space-y-4">
      <div v-for="item in feedbackList" :key="item.id" class="bg-white p-5 rounded-lg shadow-md border-l-4" :class="getRatingColor(item.rating)">
        <div class="flex justify-between items-center mb-2">
          <span class="font-semibold text-lg text-gray-800">Rating: {{ item.rating }} / 5</span>
          <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full uppercase">{{ item.role }}</span>
        </div>
        <p class="text-gray-700">{{ item.comments || 'Tidak ada komentar.' }}</p>
      </div>
    </div>

    <div v-else class="text-center bg-white p-10 rounded-lg shadow">
      <h2 class="text-xl font-semibold text-gray-700">Belum Ada Umpan Balik</h2>
      <p class="text-gray-500 mt-2">Saat ini belum ada umpan balik yang masuk.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const feedbackList = ref([]);
const isLoading = ref(true);
const error = ref(null);
const router = useRouter();

onMounted(async () => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  if (!token || role !== 'admin') {
    alert("Anda tidak memiliki akses ke halaman ini.");
    router.push('/dashboard/overview');
    return;
  }

  try {
    const res = await fetch("/api/feedback", {
      headers: { "Authorization": "Bearer " + token }
    });

    if (!res.ok) throw new Error("Gagal mengambil data umpan balik.");
    
    feedbackList.value = await res.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
});

const getRatingColor = (rating) => {
  if (rating >= 4) return 'border-green-500';
  if (rating >= 3) return 'border-yellow-500';
  return 'border-red-500';
};
</script>