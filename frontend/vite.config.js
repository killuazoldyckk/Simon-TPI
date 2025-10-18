import { defineConfig } from 'vite'
import tailwindcss from "@tailwindcss/vite";
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],
  optimizeDeps: {
    include: ['chart.js', 'vue-chartjs']
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/]
    }
  }
})
