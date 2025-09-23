<template>
  <div class="w-64 h-screen bg-blue-900 text-blue-100 flex flex-col fixed md:relative">
    <div class="h-16 flex items-center justify-center px-4 shadow-md bg-blue-950">
      <h2 class="text-2xl font-bold text-white">SIMON TPI</h2>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
      <div v-for="item in menuItems" :key="item.name">
        <router-link
          v-if="!item.children"
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

<script setup>
import { ref } from 'vue';

// --- SVG Icons (using Heroicons) ---
const iconHome = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6-4a1 1 0 001-1v-1a1 1 0 10-2 0v1a1 1 0 001 1z"></path></svg>`;
const iconUpload = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>`;
const iconList = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>`;
const iconFeedback = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>`; // <-- Ikon baru

// --- Menu data structure ---
// This now links to the routes we will define in the router.
const menuItems = ref([
  { name: 'Dashboard', icon: iconHome, path: '/dashboard/overview' },
  { name: 'Upload Manifest', icon: iconUpload, path: '/dashboard/upload' },
  { name: 'Lihat Manifest', icon: iconList, path: '/dashboard/manifests' },
  { name: 'Survei Kepuasan', icon: iconFeedback, path: '/dashboard/survey' }, // <-- Item menu baru
]);
</script>