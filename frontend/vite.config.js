import { defineConfig } from 'vite'
import tailwindcss from "@tailwindcss/vite";
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // <-- UBAH DI SINI
        changeOrigin: true,
      },
    },
  },
  optimizeDeps: {
    include: ['chart.js', 'vue-chartjs']
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/]
    }
  }
})
