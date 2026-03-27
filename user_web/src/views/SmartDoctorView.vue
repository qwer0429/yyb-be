<template>
  <div class="smart-doctor-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <el-icon :size="28" color="#fff"><FirstAidKit /></el-icon>
        </div>
        <div class="header-info">
          <h1 class="page-title">智能医生</h1>
          <p class="page-desc">AI 智能问诊助手，为您提供专业的健康咨询建议</p>
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
          <el-button 
            :icon="isFullscreen ? FullScreen : FullScreen" 
            circle 
            @click="toggleFullscreen"
          >
            <el-icon><component :is="isFullscreen ? Crop : FullScreen" /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <el-skeleton :rows="10" animated />
      <div class="loading-text">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在加载智能医生...</span>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="loadError" class="error-container">
      <el-icon :size="64" color="#F56C6C"><WarningFilled /></el-icon>
      <h3>加载失败</h3>
      <p>无法连接到智能医生服务，请检查网络后重试</p>
      <el-button type="primary" @click="refreshPage" :icon="Refresh">
        重新加载
      </el-button>
    </div>

    <!-- iframe 容器 -->
    <div v-show="!isLoading && !loadError" class="iframe-container" :class="{ 'fullscreen': isFullscreen }">
      <iframe
        ref="iframeRef"
        :src="iframeSrc"
        class="smart-doctor-iframe"
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
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  FirstAidKit,
  Refresh,
  FullScreen,
  Crop,
  Loading,
  WarningFilled,
  Close
} from '@element-plus/icons-vue'

const iframeRef = ref<HTMLIFrameElement | null>(null)
const isLoading = ref(true)
const loadError = ref(false)
const isFullscreen = ref(false)
const iframeSrc = 'http://192.168.50.20:3020/chat/share?shareId=nb0tltj2x1624ovex4t8d8rz'

// 处理 iframe 加载完成
const handleLoad = () => {
  isLoading.value = false
  loadError.value = false
}

// 处理 iframe 加载错误
const handleError = () => {
  isLoading.value = false
  loadError.value = true
  ElMessage.error('智能医生加载失败')
}

// 刷新页面
const refreshPage = () => {
  isLoading.value = true
  loadError.value = false
  if (iframeRef.value) {
    iframeRef.value.src = iframeSrc
  }
}

// 切换全屏
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    ElMessage.success('已进入全屏模式，按 ESC 或点击提示退出')
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
.smart-doctor-page {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
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

.smart-doctor-iframe {
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
  .smart-doctor-page {
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
