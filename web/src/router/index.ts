import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/drugs',
    name: 'drugs',
    component: () => import('../views/DrugListView.vue'),
    meta: { title: '药品管理' }
  },
  {
    path: '/categories',
    name: 'categories',
    component: () => import('../views/CategoryView.vue'),
    meta: { title: '分类管理' }
  },
  {
    path: '/manufacturers',
    name: 'manufacturers',
    component: () => import('../views/ManufacturerView.vue'),
    meta: { title: '厂商管理' }
  },
  {
    path: '/cabinets',
    name: 'cabinets',
    component: () => import('../views/MedicineCabinetView.vue'),
    meta: { title: '智慧药箱' }
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('../views/UserManagementView.vue'),
    meta: { title: '用户管理' }
  },
  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 医药宝` : '医药宝管理系统'
  
  // 检查 URL 中是否有 portal_token 参数（来自 iframe 门户的单点登录）
  const urlParams = new URLSearchParams(window.location.search)
  const portalToken = urlParams.get('portal_token')
  const fromPortal = urlParams.get('from') === 'portal'
  
  // 如果 URL 中有 portal_token 且当前未登录，尝试自动登录
  if (portalToken && !authStore.isAuthenticated) {
    const success = await authStore.autoLoginFromToken(portalToken)
    if (success) {
      // 清除 URL 中的 token 参数，防止刷新时重复处理
      const newUrl = window.location.pathname + window.location.hash
      window.history.replaceState({}, '', newUrl)
      
      // 如果是从门户跳转来的，显示欢迎消息
      if (fromPortal) {
        ElMessage.success('已通过门户单点登录')
      }
      
      next()
      return
    } else {
      // 自动登录失败，继续正常流程
    }
  }
  
  // 公开页面直接放行
  if (to.meta.public) {
    // 已登录用户访问登录页，重定向到首页
    if (authStore.isAuthenticated && to.path === '/login') {
      next('/')
      return
    }
    next()
    return
  }
  
  // 需要登录的页面
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    next('/login')
    return
  }
  
  next()
})

export default router
