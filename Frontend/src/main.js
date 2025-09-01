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

// 注释掉自动初始化，改为在需要时手动初始化
// import { useAuthStore } from './stores/auth'
// setTimeout(() => {
//   const authStore = useAuthStore()
//   authStore.initialize()
// }, 0)
