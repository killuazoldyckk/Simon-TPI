import { defineConfig } from 'vite'
import tailwindcss from "@tailwindcss/vite";
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],
  server: {
    allowedHosts: ['localhost', 'frontend'],
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true
    }
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
