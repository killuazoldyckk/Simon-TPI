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
          <p class="mt-1 text-sm text-gray-500">Silakan masuk ke akun Anda</p>
        </div>

      <!-- Email -->
      <div class="mb-4">
        <label for="email" class="mb-1 block text-sm font-medium text-gray-700">
          Email
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
            v-model="email" 
            id="email" 
            type="email" 
            placeholder="nama@email.com"
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
              alt="Email" 
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
        <div class="mt-2 text-right">
          <a href="#" class="text-xs text-blue-600 hover:underline">
            Lupa password?
          </a>
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


<script>
import pelabuhanImage from '../assets/pelabuhan-img.jpg';
import emailIcon from '../assets/mail.png';
import passwordIcon from '../assets/padlock.png';

export default {
  data() {
    return { 
      email: "", 
      password: "",
      backgroundImageUrl: pelabuhanImage,
      emailIconUrl: emailIcon,
      passwordIconUrl: passwordIcon,};
  },
  methods: {
    async login() {
      try {
        const res = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: this.email, password: this.password }),
        });
        
        if (res.ok) {
          const data = await res.json();
          // --- PERUBAHAN DI SINI ---
          // Simpan JWT token dan role
          localStorage.setItem("token", data.access_token); // Ganti dari data.token
          localStorage.setItem("role", data.role);           // Simpan role
          // ------------------------
          this.$router.push("/dashboard/overview");
        } else {
          alert("Login gagal. Periksa kembali email dan password.");
        }
      } catch (err) {
        console.error("Login error:", err);
        alert("Terjadi kesalahan jaringan saat mencoba login.");
      }
    },
  },
};
</script>