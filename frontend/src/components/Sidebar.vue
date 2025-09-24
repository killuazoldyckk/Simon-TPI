<script setup>
import { ref, onMounted, computed } from 'vue';
import logoSIMON from '../assets/logo_SIMON.png';

const isAdmin = ref(false);
const isAgen = ref(false);
const profile = ref({ name: '', photo_url: '' });

// **LOGIKA YANG DIPERBAIKI**
const photoSrc = computed(() => {
  if (!profile.value.photo_url) {
    return ''; // Kembalikan string kosong jika tidak ada URL foto
  }

  // Jika URL adalah untuk gambar yang diunggah pengguna (disimpan di public)
  if (profile.value.photo_url.startsWith('user_images/')) {
    // Path untuk file di folder 'public' adalah path absolut dari root
    return `/${profile.value.photo_url}`;
  } 
  // Jika tidak, itu adalah aset bawaan (disimpan di src/assets)
  else {
    // Gunakan new URL() agar Vite dapat menyelesaikan path aset dengan benar
    return new URL(`../assets/${profile.value.photo_url}`, import.meta.url).href;
  }
});
onMounted(async () => {
  isAdmin.value = localStorage.getItem('role') === 'admin';
  isAgen.value = localStorage.getItem('role') === 'agen';
  const token = localStorage.getItem("token");
  if (!token) return;

  // Fetch profile data to display in the sidebar
  try {
    const res = await fetch("/api/profile", {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (res.ok) {
      profile.value = await res.json();
    }
  } catch (err) {
    console.error("Failed to fetch profile for sidebar:", err);
  }
});

// --- SVG Icons (using Heroicons) ---
const iconHome = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6-4a1 1 0 001-1v-1a1 1 0 10-2 0v1a1 1 0 001 1z"></path></svg>`;
const iconUpload = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>`;
const iconList = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>`;
const iconFeedback = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>`; // <-- Ikon baru
const iconAddUser = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>`;
const iconFeedbackList = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z" /></svg>`;

// --- Menu data structure ---
// This now links to the routes we will define in the router.
const menuItems = ref([
  { name: 'Dashboard', icon: iconHome, path: '/dashboard/overview' },
  { name: 'Upload Manifest', icon: iconUpload, path: '/dashboard/upload', agenOnly: true }, // <-- Hanya agen yang bisa lihat
  { name: 'Lihat Manifest', icon: iconList, path: '/dashboard/manifests' },
  { name: 'Survei Kepuasan', icon: iconFeedback, path: '/dashboard/survey' },
  { name: 'Lihat Feedback', icon: iconFeedbackList, path: '/dashboard/feedback', adminOnly: true }, // <-- Tambahkan properti adminOnly
  { name: 'Tambah Pengguna', icon: iconAddUser, path: '/dashboard/add-user', adminOnly: true }, // <-- Item menu baru

]);
</script>

<template>
  <div class="w-64 h-screen bg-blue-900 text-blue-100 flex flex-col fixed md:relative">
    <div class="h-16 flex items-center justify-center px-4 shadow-md bg-blue-950">
      <img :src="logoSIMON" alt="Logo SIMON" class="w-8 h-8 mr-3" />
      <h2 class="text-2xl font-bold text-white">SIMON TPI</h2>
    </div>

    <div v-if="profile.name" class="p-4 flex flex-col items-center">
      <img :src="photoSrc" alt="Foto Profil" class="object-cover mb-2 ">
      <div class="font-medium text-white text-center">{{ profile.name }}</div>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
      <div v-for="item in menuItems" :key="item.name">
        <router-link
          v-if="(!item.adminOnly && !item.agenOnly) || (item.adminOnly && isAdmin) || (item.agenOnly && isAgen)"
          :to="item.path"
          class="flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200 hover:bg-blue-800 hover:text-white"
          active-class="bg-blue-700 text-white font-semibold shadow-inner"
        >
          <span v-html="item.icon" class="w-6 h-6"></span>
          <span>{{ item.name }}</span>
        </router-link>

        </div>
    </nav>
  </div>
</template>

