import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './index.css'

const app = createApp(App)
const pinia = createPinia() // Buat instance Pinia

app.use(router)
app.use(pinia) // Gunakan Pinia
app.mount('#app')