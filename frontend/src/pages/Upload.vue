<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h1 class="text-xl font-semibold text-blue-900 mb-4">Upload Manifest Baru</h1>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">
      {{ error }}
    </div>
    <div v-if="loading" class="bg-blue-100 text-blue-700 p-3 rounded mb-4 text-sm">
      Uploading...
    </div>

    <form @submit.prevent="uploadFile" class="space-y-4">
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Nama Kapal</label>
          <input v-model="form.ship_name" type="text" placeholder="Cth: MV. Indomal"
                 class="mt-1 border p-2 w-full rounded-md" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Bendera</label>
          <input v-model="form.flag" type="text" placeholder="Cth: Indonesia"
                 class="mt-1 border p-2 w-full rounded-md" required />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Nama Nakhoda (Skipper)</label>
          <input v-model="form.skipper_name" type="text" placeholder="Cth: Capt. Ahmad"
                 class="mt-1 border p-2 w-full rounded-md" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Pelabuhan Asal (Origin)</label>
          <input v-model="form.origin" type="text" placeholder="Cth: Port Klang"
                 class="mt-1 border p-2 w-full rounded-md" required />
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Tanggal Tiba (Arrival)</label>
          <input v-model="form.arrival_date" type="date"
                 class="mt-1 border p-2 w-full rounded-md" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Tanggal Berangkat (Departure)</label>
          <input v-model="form.departure_date" type="date"
                 class="mt-1 border p-2 w-full rounded-md" required />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Pelabuhan Tujuan (Destination)</label>
          <input v-model="form.destination" type="text" placeholder="Cth: Tanjungbalai Asahan"
                 class="mt-1 border p-2 w-full rounded-md" required />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">File Manifest (.xlsx)</label>
        <input type="file" @change="handleFile" accept=".xlsx"
               class="mt-1 block w-full text-sm text-gray-900
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-md file:border-0
                      file:text-sm file:font-semibold
                      file:bg-blue-50 file:text-blue-700
                      hover:file:bg-blue-100" required />
      </div>

      <div class="pt-2 text-right">
        <button type="submit" :disabled="!file || loading"
                class="bg-blue-600 text-white px-6 py-2 w-full md:w-auto rounded-md hover:bg-blue-700 transition-colors
                       disabled:bg-gray-400 disabled:cursor-not-allowed">
          {{ loading ? 'Processing...' : 'Upload Manifest' }}
        </button>
      </div>
      
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const file = ref(null);
const loading = ref(false);
const error = ref(null);

const form = ref({
  ship_name: '',
  flag: '',
  skipper_name: '',
  arrival_date: '',
  departure_date: '',
  origin: '',
  destination: '',
});

const handleFile = (e) => {
  file.value = e.target.files[0];
};

const uploadFile = async () => {
  loading.value = true;
  error.value = null;

  const token = localStorage.getItem("token");
  if (!token) {
    error.value = "Sesi tidak valid. Silakan login kembali.";
    loading.value = false;
    router.push("/");
    return;
  }

  if (!file.value) {
    error.value = "Silakan pilih file manifest untuk di-upload.";
    loading.value = false;
    return;
  }

  const formData = new FormData();
  formData.append("file", file.value);
  formData.append("ship_name", form.value.ship_name);
  formData.append("flag", form.value.flag);
  formData.append("skipper_name", form.value.skipper_name);
  formData.append("arrival_date", form.value.arrival_date);
  formData.append("departure_date", form.value.departure_date);
  formData.append("origin", form.value.origin);
  formData.append("destination", form.value.destination);

  const authToken = token.startsWith("Bearer ") ? token : "Bearer " + token;

  try {
    const response = await fetch("/api/manifests/upload", {
      method: "POST",
      headers: {
        Authorization: authToken
      },
      body: formData,
    });

    // --- UPDATED ERROR HANDLING BLOCK ---
    if (!response.ok) {
      let errorMsg = response.statusText; // Default error
      
      try {
        // Check if the response is actually JSON before parsing
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          // It is JSON, we can parse it for the "detail" message
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg;
        } else {
          // It's NOT JSON (it's probably the HTML crash report)
          // Read it as text to prevent the JSON.parse error
          const rawErrorText = await response.text();
          console.error("Server returned a non-JSON error response:", rawErrorText);
          errorMsg = `Server error. Check console for details. (Status: ${response.status})`;
        }
      } catch (e) {
        // Catch parsing errors
        console.error("Could not parse error response:", e);
        errorMsg = `Could not parse error response. (Status: ${response.status})`;
      }

      error.value = "Upload gagal: " + errorMsg;
      loading.value = false;
      return;
    }
    // ------------------------------------

    // Success!
    loading.value = false;
    alert("Upload manifest berhasil!");
    router.push("/dashboard/manifests"); 

  } catch (err) {
    console.error("Network or fetch error:", err);
    error.value = "Terjadi kesalahan jaringan saat meng-upload file.";
    loading.value = false;
  }
};
</script>