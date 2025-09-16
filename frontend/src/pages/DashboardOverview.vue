<template>
  <div>
    <div v-if="isLoading" class="text-center text-gray-500">
      Loading analytics...
    </div>

    <div v-else-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
      <p class="font-bold">Error</p>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      
      <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-600">
        <h3 class="text-lg font-semibold text-gray-700">Total Penumpang</h3>
        <p class="text-4xl font-bold text-blue-900 mt-2">{{ stats.total_passengers }}</p>
      </div>

      <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
        <h3 class="text-lg font-semibold text-gray-700">Total Manifest (Kapal)</h3>
        <p class="text-4xl font-bold text-green-700 mt-2">{{ stats.total_manifests }}</p>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
        <h3 class="text-lg font-semibold text-gray-700">Demografi Penumpang</h3>
        <div class="mt-2 space-y-1">
           <p class="text-2xl font-semibold text-gray-800">
             <span class="text-blue-700">{{ stats.male_passengers }}</span> Laki-laki
           </p>
           <p class="text-2xl font-semibold text-gray-800">
             <span class="text-pink-600">{{ stats.female_passengers }}</span> Perempuan
           </p>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-600">
        <h3 class="text-lg font-semibold text-gray-700">Kebangsaan Teratas</h3>
        <p class="text-4xl font-bold text-purple-900 mt-2">
          {{ stats.top_nationality.nationality }}
        </p>
        <p class="text-sm text-gray-600">
          ({{ stats.top_nationality.count }} orang)
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const stats = ref(null);
const isLoading = ref(true);
const error = ref(null);
const router = useRouter();

onMounted(async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Sesi tidak valid, silahkan login kembali.");
    router.push('/');
    return;
  }
  
  const authToken = token.startsWith("Bearer ") ? token : "Bearer " + token;

  try {
    const res = await fetch("/api/analytics/overview", {
      headers: {
        "Authorization": authToken
      }
    });

    if (!res.ok) {
      if (res.status === 401) {
        throw new Error("Sesi Anda telah berakhir. Silahkan login kembali.");
      }
      throw new Error("Gagal mengambil data analytics.");
    }

    stats.value = await res.json();
  } catch (err) {
    error.value = err.message;
    if (err.message.includes("Sesi")) {
        router.push('/');
    }
  } finally {
    isLoading.value = false;
  }
});
</script>