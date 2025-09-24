<template>
  <div class="bg-white p-8 rounded-2xl shadow-lg max-w-lg mx-auto ring-1 ring-gray-200">
    <h1 class="text-2xl font-bold text-blue-900 mb-6">Tambah Pengguna Baru</h1>

    <div v-if="successMessage" class="bg-green-100 text-green-700 p-3 rounded mb-4">{{ successMessage }}</div>
    <div v-if="error" class="bg-red-100 text-red-700 p-3 rounded mb-4">{{ error }}</div>

    <form @submit.prevent="submitUser" class="space-y-4">
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700">Nama Lengkap</label>
        <input v-model="form.name" type="text" id="name" class="mt-1 border p-2 w-full rounded-md shadow-sm" required>
      </div>

      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
        <input v-model="form.email" type="email" id="email" class="mt-1 border p-2 w-full rounded-md shadow-sm" required>
      </div>
       <div>
        <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
        <input v-model="form.password" type="password" id="password" class="mt-1 border p-2 w-full rounded-md shadow-sm" required>
      </div>

      <div>
        <label for="role" class="block text-sm font-medium text-gray-700">Role</label>
        <select v-model="form.role" id="role" class="mt-1 border p-2 w-full rounded-md shadow-sm bg-white" required>
          <option value="agen">Agen</option>
          <option value="admin">Admin</option>
          <option value="stakeholders">Stakeholders</option>
        </select>
      </div>

      <div>
        <label for="photo" class="block text-sm font-medium text-gray-700">Foto Profil</label>
        <input @change="handleFileUpload" type="file" id="photo" class="mt-1 block w-full text-sm text-gray-500
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-full file:border-0
                      file:text-sm file:font-semibold
                      file:bg-blue-50 file:text-blue-700
                      hover:file:bg-blue-100" required>
      </div>

      <div class="pt-4 text-right">
        <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors shadow-md">
          Tambah Pengguna
        </button>
      </div>
    </form>
  </div>
</template>


<script setup>
import { ref } from 'vue';

const form = ref({
  name: '',
  email: '',
  password: '',
  role: 'agen',
});
const photoFile = ref(null);
const error = ref(null);
const successMessage = ref(null);

const handleFileUpload = (event) => {
  photoFile.value = event.target.files[0];
};

const submitUser = async () => {
  error.value = null;
  successMessage.value = null;
  const token = localStorage.getItem("token");

  // Buat FormData untuk mengirim file dan data
  const formData = new FormData();
  formData.append('name', form.value.name);
  formData.append('email', form.value.email);
  formData.append('password', form.value.password);
  formData.append('role', form.value.role);
  if (photoFile.value) {
    formData.append('photo', photoFile.value);
  }

  try {
    const res = await fetch("/api/users", {
      method: 'POST',
      headers: {
        // 'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Gagal membuat pengguna.");
    
    successMessage.value = data.message;
    // Reset form
    form.value = { name: '', email: '', password: '', role: 'agen' };
    // Anda mungkin juga perlu mereset input file, tetapi ini sedikit lebih rumit di Vue.
    // Untuk saat ini, kita biarkan saja.

  } catch (err) {
    error.value = err.message;
  }
};
</script>