<template>
  <div class="flex h-screen items-center justify-center bg-gradient-to-br from-gray-100 via-gray-200 to-gray-300">
    <div class="w-1/2 h-full hidden md:block"
      :style="{ 
        backgroundImage: 'url(' + backgroundImageUrl + ')',
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }">
      
    </div>
    
    <div class="w-1/2 md:w-1/2 h-full flex items-center justify-center bg-gray-100 p-8">
      <form 
      @submit.prevent="login" 
      class="w-full max-w-sm rounded-2xl bg-white p-8 shadow-lg ring-1 ring-gray-200"
      >
        <!-- Logo / Title -->
        <div class="mb-6 text-center">
          <h1 class="text-3xl font-extrabold text-blue-600 tracking-tight">
            SIMON TPI
          </h1>
          <h2 class="text-l font-semibold text-blue-600 tracking-tight">
            Sistem Informasi Manifes Online di TPI
          </h2>
          <p class="mt-2 text-sm text-gray-500">Silakan masuk ke akun Anda</p>
        </div>

      <!-- Email -->
      <div class="mb-4">
        <label for="user" class="mb-1 block text-sm font-medium text-gray-700">
          Username
        </label>
        <div class="relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
            <img 
              :src="emailIconUrl" 
              alt="Email" 
              class="h-5 w-5" 
            /> 
          </span>
          <input 
            v-model="username" 
            id="username" 
            type="text" 
            placeholder="Username"
            class="w-full rounded-md border border-gray-300 pl-10 pr-3 py-2 shadow-sm 
                   @focus:border-blue-500 @focus:ring-2 @focus:ring-blue-500 @focus:outline-none"
            required
          />
        </div>
      </div>

      <!-- Password -->
      <div class="mb-6">
        <label for="password" class="mb-1 block text-sm font-medium text-gray-700">
          Password
        </label>
        <div class="relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
            <img 
              :src="passwordIconUrl" 
              alt="password" 
              class="h-5 w-5" 
            /> 
          </span>
          <input 
            v-model="password" 
            id="password" 
            type="password" 
            placeholder="••••••••"
            class="w-full rounded-md border border-gray-300 pl-10 pr-3 py-2 shadow-sm 
                   focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            required
          />
        </div>
      </div>

      <!-- Submit Button -->
      <button 
        type="submit"
        class="w-full rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white shadow-md 
               transition duration-200 ease-in-out hover:bg-blue-700 focus:outline-none 
               focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Login
      </button>
      </form>
    </div>
    
  </div>
</template>


<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// --- Aset & Gambar (sama seperti sebelumnya) ---
import pelabuhanImage from '../assets/pelabuhan-img.jpg';
import emailIcon from '../assets/user.png';
import passwordIcon from '../assets/padlock.png';

// --- State Management ---
const username = ref("");
const password = ref("");
const authStore = useAuthStore();
const router = useRouter();

// Variabel untuk template
const backgroundImageUrl = pelabuhanImage;
const emailIconUrl = emailIcon;
const passwordIconUrl = passwordIcon;

// --- Fungsi Login yang Diperbarui ---
// ...existing code...
const login = async () => {
  try {
    const apiBase = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
    const apiUrl = `${apiBase}/api/login`;
    
    // Siapkan data dalam format URL-encoded yang benar
    const details = {
        'username': username.value,
        'password': password.value
    };
    const formBody = Object.keys(details).map(key => 
        encodeURIComponent(key) + '=' + encodeURIComponent(details[key])
    ).join('&');
    
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { 
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formBody,
    });

    // Handle non-OK responses safely (don't call response.json() on empty/non-JSON body)
    if (!response.ok) {
      const text = await response.text();
      let errMsg = text || "Login gagal. Periksa kembali username dan password Anda.";
      try {
        const parsed = JSON.parse(text || "{}");
        errMsg = parsed.detail || parsed.message || errMsg;
      } catch (e) {
        // leave errMsg as-is (plain text or empty)
      }
      throw new Error(errMsg);
    }

    const data = await response.json();

    // Gunakan store Pinia untuk menyimpan token dan role
    authStore.setToken(data.access_token, data.role);
    
    // Arahkan ke dashboard setelah berhasil
    router.push("/dashboard/overview");

  } catch (error) {
    alert(error.message);
  }
};
// ...existing code...
</script>