import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

const authStore = useAuthStore()

// 若从管理端退出跳转而来，强制清除登录状态（无论 token 是否有效）
const urlParams = new URLSearchParams(window.location.search)
if (urlParams.get('from') === 'admin_logout') {
  authStore.logout()
  // 清除 URL 参数，避免刷新时重复处理
  const newUrl = window.location.pathname + window.location.hash
  window.history.replaceState({}, '', newUrl)
} else {
  // 正常初始化认证状态
  authStore.initAuth()
}

app.mount('#app')
