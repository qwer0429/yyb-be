import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
    meta: { public: true, title: '注册' }
  },
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
    meta: { title: '首页', permission: 'user_portal' }
  },
  {
    path: '/drugs',
    name: 'drugs',
    component: () => import('../views/DrugBrowseView.vue'),
    meta: { title: '药品浏览', permission: 'user_portal' }
  },
  {
    path: '/categories',
    name: 'categories',
    component: () => import('../views/CategoryBrowseView.vue'),
    meta: { title: '分类浏览', permission: 'user_portal' }
  },
  {
    path: '/cabinets',
    name: 'cabinets',
    component: () => import('../views/MedicineCabinetView.vue'),
    meta: { title: '我的药箱', permission: 'user_portal' }
  },
  {
    path: '/smart-doctor',
    name: 'smart-doctor',
    component: () => import('../views/SmartDoctorView.vue'),
    meta: { title: '智能医生', permission: 'smart_doctor' }
  },
  {
    path: '/system/:key',
    name: 'system-portal',
    component: () => import('../views/SystemPortalView.vue'),
    meta: { title: '系统门户' }
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
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} | 医药宝` : '医药宝'
  
  // 公开页面直接放行
  if (to.meta.public) {
    // 已登录用户访问登录页或注册页，重定向到首页
    if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
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
  
  // 权限检查：如果路由配置了 permission，检查用户是否有权限
  const requiredPermission = to.meta.permission as string | undefined
  if (requiredPermission && !authStore.hasPermission(requiredPermission)) {
    ElMessage.warning('您没有权限访问该页面')
    next('/')
    return
  }
  
  next()
})

export default router
