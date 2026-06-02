<template>
  <div class="system-portal-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" :style="{ background: currentSystem?.gradient || 'linear-gradient(135deg, #409EFF 0%, #79bbff 100%)' }">
          <el-icon :size="24" color="#fff"><component :is="currentSystem?.icon || Monitor" /></el-icon>
        </div>
        <div class="header-info">
          <h1 class="page-title">{{ currentSystem?.title || '系统门户' }}</h1>
          <p class="page-desc">{{ currentSystem?.desc || '正在加载外部系统...' }}</p>
        </div>
      </div>
      <div class="header-actions">
        <el-tooltip content="刷新页面" placement="bottom">
          <el-button 
            :icon="Refresh" 
            circle 
            @click="refreshPage"
            :loading="isLoading"
          />
        </el-tooltip>
        <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏模式'" placement="bottom">
          <el-button circle @click="toggleFullscreen">
            <el-icon><component :is="isFullscreen ? Crop : FullScreen" /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="在新窗口打开" placement="bottom">
          <el-button :icon="Link" circle @click="openInNewWindow" />
        </el-tooltip>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <el-skeleton :rows="10" animated />
      <div class="loading-text">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在加载 {{ currentSystem?.title || '系统' }}...</span>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="loadError" class="error-container">
      <el-icon :size="64" color="#F56C6C"><WarningFilled /></el-icon>
      <h3>加载失败</h3>
      <p>无法连接到 {{ currentSystem?.title || '目标系统' }}，请检查网络后重试</p>
      <el-button type="primary" @click="refreshPage" :icon="Refresh">
        重新加载
      </el-button>
    </div>

    <!-- 无权限状态 -->
    <div v-else-if="!hasAccess" class="error-container">
      <el-icon :size="64" color="#E6A23C"><WarningFilled /></el-icon>
      <h3>暂无权限</h3>
      <p>您没有访问该系统的权限，请联系管理员开通</p>
      <el-button type="primary" @click="$router.push('/')" :icon="HomeFilled">
        返回首页
      </el-button>
    </div>

    <!-- iframe 容器 -->
    <div v-show="!isLoading && !loadError && hasAccess" class="iframe-container" :class="{ 'fullscreen': isFullscreen }">
      <iframe
        ref="iframeRef"
        :src="iframeSrcWithToken"
        class="system-iframe"
        frameborder="0"
        allow="*"
        @load="handleLoad"
        @error="handleError"
      ></iframe>
    </div>

    <!-- 全屏提示 -->
    <div v-if="isFullscreen" class="exit-fullscreen-hint" @click="toggleFullscreen">
      <el-icon><Close /></el-icon>
      <span>点击退出全屏</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  FullScreen,
  Crop,
  Loading,
  WarningFilled,
  Close,
  Monitor,
  Link,
  HomeFilled,
  FirstAidKit,
  Management
} from '@element-plus/icons-vue'
import type { Component } from 'vue'

// 系统配置
interface SystemConfig {
  key: string
  title: string
  desc: string
  url: string
  icon: Component
  gradient: string
  permission: string
}

const SYSTEM_CONFIGS: SystemConfig[] = [
  {
    key: 'admin',
    title: '后台管理系统',
    desc: '医药宝后台管理，提供药品、用户、数据统计等管理功能',
    url: import.meta.env.VITE_ADMIN_URL || `http://${import.meta.env.VITE_SERVICE_HOST || 'localhost'}:${import.meta.env.VITE_ADMIN_PORT || '5173'}`,
    icon: Management,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    permission: 'admin_system'
  },
  {
    key: 'smart-doctor',
    title: '智能医生',
    desc: 'AI 智能问诊助手，为您提供专业的健康咨询建议',
    // url: 'http://192.168.50.20:3020/chat/share?shareId=nb0tltj2x1624ovex4t8d8rz',
    url: 'http://192.168.50.20:3020/chat/share?shareId=nb0tltj2x1624ovex4t8d8rz',
    icon: FirstAidKit,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    permission: 'smart_doctor'
  }
]

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const iframeRef = ref<HTMLIFrameElement | null>(null)
const isLoading = ref(true)
const loadError = ref(false)
const isFullscreen = ref(false)

const systemKey = computed(() => route.params.key as string)

const currentSystem = computed(() => {
  return SYSTEM_CONFIGS.find(s => s.key === systemKey.value)
})

// 检查是否有权限访问该系统
const hasAccess = computed(() => {
  if (!currentSystem.value) return false
  return authStore.hasPermission(currentSystem.value.permission)
})

// iframe 地址（附加 token 用于单点登录）
const iframeSrcWithToken = computed(() => {
  if (!currentSystem.value) return ''
  const baseUrl = currentSystem.value.url
  const token = authStore.accessToken
  
  // 如果地址已包含查询参数，使用 & 连接，否则用 ?
  const separator = baseUrl.includes('?') ? '&' : '?'
  return `${baseUrl}${separator}portal_token=${token}&from=portal`
})

// 处理 iframe 加载完成
const handleLoad = () => {
  isLoading.value = false
  loadError.value = false
}

// 处理 iframe 加载错误
const handleError = () => {
  isLoading.value = false
  loadError.value = true
  ElMessage.error(`${currentSystem.value?.title || '系统'}加载失败`)
}

// 刷新页面
const refreshPage = () => {
  isLoading.value = true
  loadError.value = false
  if (iframeRef.value) {
    iframeRef.value.src = iframeSrcWithToken.value
  }
}

// 切换全屏
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    ElMessage.success('已进入全屏模式，按 ESC 或点击提示退出')
  }
}

// 在新窗口打开
const openInNewWindow = () => {
  if (currentSystem.value) {
    window.open(iframeSrcWithToken.value, '_blank')
  }
}

// 监听 ESC 键退出全屏
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && isFullscreen.value) {
    isFullscreen.value = false
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  // 设置加载超时检查
  setTimeout(() => {
    if (isLoading.value) {
      console.log('iframe 加载中...')
    }
  }, 10000)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.system-portal-page {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.header-info {
  color: #fff;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 6px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-desc {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.header-actions :deep(.el-button) {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: #fff;
  transition: all 0.3s ease;
}

.header-actions :deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

/* 加载状态 */
.loading-container {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-text {
  text-align: center;
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 错误状态 */
.error-container {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  text-align: center;
}

.error-container h3 {
  font-size: 20px;
  color: #303133;
  margin: 8px 0 0 0;
}

.error-container p {
  color: #909399;
  margin: 0 0 16px 0;
}

/* iframe 容器 */
.iframe-container {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;
  transition: all 0.3s ease;
}

.iframe-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  border-radius: 0;
}

.system-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

/* 退出全屏提示 */
.exit-fullscreen-hint {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  padding: 10px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.exit-fullscreen-hint:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: translateY(-2px);
}

/* 响应式 */
@media (max-width: 768px) {
  .system-portal-page {
    height: calc(100vh - 100px);
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .header-left {
    flex-direction: column;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .page-desc {
    font-size: 12px;
  }
}
</style>
