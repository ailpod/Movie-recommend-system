import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')

// 在应用挂载后初始化认证状态
import { useAuthStore } from './stores/auth'
setTimeout(() => {
  const authStore = useAuthStore()
  authStore.initialize()
}, 0)
