<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-6xl mx-auto">
      
      <div v-if="!manifest" class="bg-white p-8 rounded-lg shadow text-center text-gray-500">
        Loading manifest details...
      </div>

      <div v-else>
        <div class="bg-white rounded-lg shadow overflow-hidden mb-6">
          <div class="p-5 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h1 class="text-2xl font-bold text-gray-800">Detail Manifest: {{ manifest.ship_name }}</h1>
              <p class="text-gray-600">Tiba pada: {{ manifest.voyage_date }}</p>
            </div>
            <button
              v-if="manifest.minio_object_name"
              @click="downloadManifestFile"
              class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors text-sm font-semibold"
            >
              Download File Asli
            </button>
            </div>
          </div>

        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const manifest = ref(null);
const route = useRoute();
const router = useRouter();

// --- FUNGSI BARU UNTUK DOWNLOAD ---
const downloadManifestFile = async () => {
  const token = localStorage.getItem("token");
  if (!manifest.value || !token) return;

  try {
    const res = await fetch(`/api/manifests/${manifest.value.id}/download`, {
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (!res.ok) {
      throw new Error("Gagal mendapatkan link download.");
    }

    const data = await res.json();
    if (data.url) {
      // Buka URL presigned dari MinIO di tab baru
      window.open(data.url, '_blank');
    }
  } catch (err) {
    alert(err.message);
    console.error(err);
  }
};
// ---------------------------------

onMounted(async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Sesi tidak valid, silahkan login kembali.");
    router.push('/');
    return;
  }

  try {
    const manifestId = route.params.id;
    const res = await fetch(`/api/manifests/${manifestId}`, {
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (!res.ok) {
       if (res.status === 401) {
         alert("Sesi Anda telah berakhir. Silahkan login kembali.");
         router.push('/');
       } else {
         alert("Gagal mengambil data detail. Sesi mungkin berakhir.");
         router.push('/dashboard/manifests'); // Kembali ke daftar
       }
       return;
    }

    manifest.value = await res.json();
  } catch (err) {
    alert("Terjadi kesalahan jaringan.");
    console.error(err);
    router.push('/dashboard/manifests');
  }
});
</script>