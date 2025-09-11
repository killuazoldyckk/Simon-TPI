import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    allowedHosts: ['localhost', 'simon-frontend'],
    host: '0.0.0.0',
    port: 5173
  }
})
