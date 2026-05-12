<template>
  <div class="app-wrapper">
    <!-- 登录/注册页单独布局（无侧边栏） -->
    <template v-if="isPublicPage">
      <router-view />
    </template>
    
    <!-- 主布局 -->
    <template v-else>
      <el-container class="layout-container">
        <!-- 侧边栏 -->
        <el-aside 
          :width="isCollapse ? '72px' : '220px'" 
          class="sidebar"
          :class="{ 'sidebar-collapsed': isCollapse }"
        >
          <div class="logo">
            <div class="logo-icon-wrapper">
              <el-icon :size="28"><FirstAidKit /></el-icon>
            </div>
            <span v-show="!isCollapse" class="logo-text">医药宝</span>
            <div v-show="!isCollapse" class="logo-badge">{{ userRoleBadge }}</div>
          </div>
          
          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapse"
            :collapse-transition="false"
            router
            class="sidebar-menu"
          >
            <template v-for="item in visibleMenuItems" :key="item.index">
              <el-menu-item :index="item.index" class="menu-item">
                <div class="menu-icon-wrapper" :class="item.colorClass">
                  <el-icon><component :is="item.icon" /></el-icon>
                </div>
                <template #title>
                  <span class="menu-title">{{ item.title }}</span>
                  <div class="menu-arrow">
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </template>
              </el-menu-item>
            </template>
          </el-menu>
          
          <!-- 侧边栏底部 -->
          <div class="sidebar-footer" v-show="!isCollapse">
            <div class="footer-line"></div>
            <p class="footer-text">医药宝{{ userRoleText }}</p>
          </div>
        </el-aside>
        
        <el-container class="main-container">
          <!-- 顶部导航栏 -->
          <el-header class="header">
            <div class="header-left">
              <div 
                class="collapse-btn" 
                @click="toggleCollapse"
                :class="{ 'is-collapsed': isCollapse }"
              >
                <el-icon :size="18">
                  <Fold v-if="!isCollapse" />
                  <Expand v-else />
                </el-icon>
              </div>
              
              <!-- 面包屑 -->
              <div class="breadcrumb">
                <el-icon :size="16" color="#909399"><HomeFilled /></el-icon>
                <span class="breadcrumb-separator">/</span>
                <span class="breadcrumb-current">{{ pageTitle }}</span>
              </div>
            </div>
            
            <div class="header-right">
              <!-- 时间显示 -->
              <div class="header-time" v-if="!isMobile">
                <el-icon><Clock /></el-icon>
                <span>{{ currentTime }}</span>
              </div>
              
              <!-- 用户菜单 -->
              <el-dropdown @command="handleCommand" placement="bottom-end">
                <div class="user-info">
                  <div class="user-avatar">
                    <el-avatar :size="36" :icon="UserFilled" />
                    <div class="user-status"></div>
                  </div>
                  <div class="user-meta" v-if="!isMobile">
                    <span class="user-name">{{ authStore.user?.name || authStore.username || '用户' }}</span>
                    <span class="user-role">{{ userRoleText }}</span>
                  </div>
                  <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu class="user-dropdown">
                    <div class="dropdown-header">
                      <el-avatar :size="48" :icon="UserFilled" />
                      <div class="dropdown-user-info">
                        <span class="dropdown-user-name">{{ authStore.user?.name || authStore.username || '用户' }}</span>
                        <span class="dropdown-user-role">{{ userRoleText }}</span>
                      </div>
                    </div>
                    <el-dropdown-item divided command="profile">
                      <el-icon><User /></el-icon>
                      <span>个人中心</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="logout" class="logout-item">
                      <el-icon><SwitchButton /></el-icon>
                      <span>退出登录</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-header>
          
          <!-- 主内容区 -->
          <el-main class="main-content">
            <div class="content-wrapper">
              <router-view v-slot="{ Component }">
                <transition name="fade-transform" mode="out-in">
                  <component :is="Component" />
                </transition>
              </router-view>
            </div>
          </el-main>
        </el-container>
      </el-container>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  FirstAidKit,
  Collection,
  Box,
  ArrowRight,
  Fold,
  Expand,
  Clock,
  UserFilled,
  ArrowDown,
  User,
  SwitchButton,
  Management
} from '@element-plus/icons-vue'
import type { Component } from 'vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)
const isMobile = ref(false)
const currentTime = ref('')
let timer: number | null = null

// 菜单配置
interface MenuItem {
  index: string
  title: string
  icon: Component
  colorClass: string
  permission: string
}

const menuItems: MenuItem[] = [
  { index: '/', title: '首页', icon: HomeFilled, colorClass: '', permission: 'user_portal' },
  { index: '/drugs', title: '药品浏览', icon: FirstAidKit, colorClass: 'blue', permission: 'user_portal' },
  { index: '/categories', title: '分类浏览', icon: Collection, colorClass: 'green', permission: 'user_portal' },
  { index: '/cabinets', title: '我的药箱', icon: Box, colorClass: 'orange', permission: 'user_portal' },
  { index: '/smart-doctor', title: '智能医生', icon: FirstAidKit, colorClass: 'purple', permission: 'smart_doctor' },
  { index: '/system/admin', title: '后台管理', icon: Management, colorClass: 'red', permission: 'admin_system' },
]

// 根据权限过滤可见菜单
const visibleMenuItems = computed(() => {
  return menuItems.filter(item => authStore.hasPermission(item.permission))
})

// 用户角色显示
const userRoleText = computed(() => {
  if (authStore.isAdmin) return '管理员'
  return '普通用户'
})

const userRoleBadge = computed(() => {
  if (authStore.isAdmin) return '管理端'
  return '用户端'
})

// 检测移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) {
    isCollapse.value = true
  }
}

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  checkMobile()
  updateTime()
  timer = window.setInterval(updateTime, 1000)
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('resize', checkMobile)
})

const isPublicPage = computed(() => route.path === '/login' || route.path === '/register')
const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/': '首页',
    '/drugs': '药品浏览',
    '/categories': '分类浏览',
    '/cabinets': '我的药箱',
    '/smart-doctor': '智能医生',
    '/system/admin': '后台管理'
  }
  return titles[route.path] || ''
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }).then(() => {
        authStore.logout()
        router.push('/login')
      })
      break
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-wrapper {
  height: 100%;
}

.layout-container {
  height: 100vh;
  background: #f5f7fa;
}

/* 侧边栏样式 - Light Theme */
.sidebar {
  background: #ffffff;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 10;
  border-right: 1px solid #e2e8f0;
}

.logo {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  position: relative;
}

.logo-icon-wrapper {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
  animation: logo-breathe 3s infinite ease-in-out;
}

@keyframes logo-breathe {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(64, 158, 255, 0.5);
  }
}

.logo-text {
  color: #1e293b;
  font-size: 20px;
  font-weight: 700;
  margin-left: 12px;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.logo-badge {
  margin-left: 8px;
  padding: 3px 10px;
  background: #e0f2fe;
  border: 1px solid #bae6fd;
  border-radius: 20px;
  color: #0284c7;
  font-size: 11px;
  font-weight: 600;
}

/* 菜单样式 */
/* 菜单样式 - Light Theme */
.sidebar-menu {
  border-right: none;
  background: transparent;
  padding: 20px 16px;
  flex: 1;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin-bottom: 12px;
  border-radius: 10px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0 16px !important;
  background: transparent;
  border-left: 3px solid transparent;
}

/* 未选中状态 - 深色文字 */
.sidebar-menu :deep(.el-menu-item) .menu-title {
  color: #475569 !important;  /* text-slate-600 */
  font-size: 15px;
  font-weight: 500;
  transition: all 0.25s ease;
}

.sidebar-menu :deep(.el-menu-item) .menu-icon-wrapper {
  color: #64748b !important;  /* text-slate-500 */
}

/* 悬停状态 */
.sidebar-menu :deep(.el-menu-item:hover) {
  background: #f1f5f9 !important;  /* slate-100 */
  transform: translateX(2px);
}

.sidebar-menu :deep(.el-menu-item:hover) .menu-title {
  color: #0f172a !important;  /* slate-900 */
}

.sidebar-menu :deep(.el-menu-item:hover) .menu-icon-wrapper {
  color: #334155 !important;  /* slate-700 */
}

/* 选中状态 - 统一使用主题色 */
.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #e0f2fe !important;  /* sky-100 */
  border-left: 3px solid #0ea5e9;  /* sky-500 */
  box-shadow: none;
}

.sidebar-menu :deep(.el-menu-item.is-active) .menu-title {
  color: #0284c7 !important;  /* sky-600 */
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item.is-active) .menu-icon-wrapper {
  color: #0284c7 !important;  /* sky-600 */
}

.menu-item {
  display: flex;
  align-items: center;
}

/* 图标样式 - Line Icons Style */
.menu-icon-wrapper {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  transition: all 0.25s ease;
  background: none !important;
  border-radius: 0;
}

.menu-icon-wrapper.blue,
.menu-icon-wrapper.green,
.menu-icon-wrapper.orange,
.menu-icon-wrapper.purple,
.menu-icon-wrapper.red {
  background: none !important;
}

.sidebar-menu :deep(.el-menu-item:hover) .menu-icon-wrapper {
  transform: scale(1.05);
}

.menu-title {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.menu-arrow {
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.25s ease;
  font-size: 14px;
  color: #94a3b8;
}

.sidebar-menu :deep(.el-menu-item:hover) .menu-arrow {
  opacity: 0.6;
  transform: translateX(0);
}

.sidebar-menu :deep(.el-menu-item.is-active) .menu-arrow {
  opacity: 1;
  color: #0284c7;
  transform: translateX(0);
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 20px;
  text-align: center;
}

.footer-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
  margin-bottom: 12px;
}

.footer-text {
  color: #94a3b8;  /* text-slate-400 */
  font-size: 12px;
}

/* 折叠状态 */
.sidebar-collapsed .logo {
  justify-content: center;
  padding: 0;
}

.sidebar-collapsed .logo-icon-wrapper {
  margin: 0;
  width: 40px;
  height: 40px;
}

/* 顶部栏样式 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 0 24px;
  height: 72px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  border-radius: 10px;
  background: #f1f5f9;
  transition: all 0.25s ease;
}

.collapse-btn:hover {
  background: #38bdf8;
  color: #fff;
  transform: scale(1.05);
}

.collapse-btn.is-collapsed {
  background: #38bdf8;
  color: #fff;
}

/* 面包屑 */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #64748b;
  font-size: 14px;
}

.breadcrumb-separator {
  color: #cbd5e1;
}

.breadcrumb-current {
  font-weight: 600;
  color: #0f172a;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-time {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 20px;
  color: #606266;
  font-size: 14px;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 12px 6px 6px;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.user-info:hover {
  background: #f5f7fa;
  border-color: #e4e7ed;
}

.user-avatar {
  position: relative;
}

.user-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  background: #67C23A;
  border: 2px solid #fff;
  border-radius: 50%;
  animation: status-pulse 2s infinite;
}

@keyframes status-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.4);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(103, 194, 58, 0);
  }
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.user-role {
  font-size: 12px;
  color: #909399;
}

.dropdown-arrow {
  color: #c0c4cc;
  transition: transform 0.3s ease;
}

.user-info:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* 下拉菜单 */
.user-dropdown {
  padding: 0;
  min-width: 220px;
  border-radius: 12px;
  overflow: hidden;
}

.dropdown-header {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #ebeef5;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dropdown-user-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.dropdown-user-role {
  font-size: 12px;
  color: #909399;
}

.user-dropdown :deep(.el-dropdown-menu__item) {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.user-dropdown :deep(.el-dropdown-menu__item:hover) {
  background: #f5f7fa;
}

.logout-item {
  color: #F56C6C;
}

.logout-item:hover {
  background: rgba(245, 108, 108, 0.1) !important;
}

/* 主内容区 */
.main-container {
  background: #f5f7fa;
}

.main-content {
  padding: 24px;
  overflow-y: auto;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面切换动画 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 100;
    transform: translateX(-100%);
  }
  
  .sidebar.sidebar-collapsed {
    transform: translateX(0);
  }
  
  .header {
    padding: 0 16px;
  }
  
  .main-content {
    padding: 16px;
  }
}
</style>
