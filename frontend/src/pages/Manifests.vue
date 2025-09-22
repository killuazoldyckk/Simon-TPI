<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-800 mb-6">Daftar Manifest</h1>

      <div v-if="isLoading" class="text-center py-10">
        <p class="text-gray-500">Loading data...</p>
      </div>

      <div v-else-if="manifests.length > 0" class="space-y-4">
        
        <router-link
          v-for="m in manifests"
          :key="m.id"
          :to="{ name: 'Detail Manifest', params: { id: m.id } }"
          class="block p-5 bg-white rounded-lg shadow border border-transparent hover:border-blue-500 hover:shadow-md transition-all duration-200"
        >
          <div class="flex justify-between items-center">
            <div>
              <div class="font-semibold text-lg text-blue-700">{{ m.ship_name }}</div>
              <div class="text-sm text-gray-600">
                Tiba: {{ m.voyage_date }} | ({{ m.passengers.length }} Penumpang)
              </div>
            </div>
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </div>
        </router-link>
      </div>

      <div v-else class="text-center bg-white p-10 rounded-lg shadow">
        <h2 class="text-xl font-semibold text-gray-700">Tidak Ada Data Manifest</h2>
        <p class="text-gray-500 mt-2">Upload manifest baru untuk melihat data di sini.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const manifests = ref([]);
const isLoading = ref(true);
const router = useRouter();

onMounted(async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Sesi tidak valid, silahkan login kembali.");
    router.push('/'); // Redirect to login if no token
    return;
  }

  try {
    const res = await fetch("/api/manifests", {
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (!res.ok) {
      if (res.status === 401) {
         alert("Sesi Anda telah berakhir. Silahkan login kembali.");
         router.push('/');
      } else {
         alert("Gagal mengambil data manifests.");
      }
      return;
    }

    manifests.value = await res.json();
  } catch (err) {
    alert("Terjadi kesalahan jaringan.");
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});
</script>