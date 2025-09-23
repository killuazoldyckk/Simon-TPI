<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h1 class="text-xl font-semibold text-blue-900 mb-4">Survei Kepuasan Pengguna</h1>
    
    <div v-if="submitted" class="bg-green-100 text-green-700 p-3 rounded mb-4 text-sm">
      Terima kasih atas waktu dan masukan yang Anda berikan!
    </div>

    <form @submit.prevent="submitSurvey" class="space-y-6" v-else>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Seberapa puaskah Anda dengan sistem SIMON TPI secara keseluruhan?
        </label>
        <div class="flex space-x-2">
          <button
            v-for="rating in 5"
            :key="rating"
            @click="form.rating = rating"
            type="button"
            :class="[
              'w-12 h-12 rounded-full text-lg font-bold transition-colors',
              form.rating >= rating ? 'bg-yellow-400 text-white' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            ]"
          >
            {{ rating }}
          </button>
        </div>
      </div>

      <div>
        <label for="comments" class="block text-sm font-medium text-gray-700">
          Apakah ada saran atau masukan untuk perbaikan di masa mendatang?
        </label>
        <textarea
          v-model="form.comments"
          id="comments"
          rows="4"
          placeholder="Tuliskan saran Anda di sini..."
          class="mt-1 border p-2 w-full rounded-md shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
        ></textarea>
      </div>

      <div class="pt-2 text-right">
        <button 
          type="submit"
          :disabled="form.rating === 0"
          class="bg-blue-600 text-white px-6 py-2 w-full md:w-auto rounded-md hover:bg-blue-700 transition-colors
                 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Kirim Umpan Balik
        </button>
      </div>
      
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const submitted = ref(false);
const error = ref(null);

const form = ref({
  rating: 0,
  comments: ''
});

const submitSurvey = async () => {
  error.value = null;
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");
  if (!token || !role) {
    error.value = "Sesi tidak valid, silakan login kembali.";
    return;
  }

  try {
    const response = await fetch("/api/survey", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
      },
      body: JSON.stringify({
        rating: form.value.rating,
        comments: form.value.comments,
        role: role // tambahkan role di sini
        }),
      });

    if (!response.ok) {
      throw new Error("Gagal mengirim umpan balik.");
    }
    
    submitted.value = true;

  } catch (err) {
    error.value = err.message;
  }
};
</script>