<template>
  <div class="home-page">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="never">
      <div class="welcome-content">
        <div class="welcome-text">
          <div class="greeting">
            <span class="greeting-icon">👋</span>
            <h1>{{ greeting }}，{{ authStore.user?.name || authStore.username || '用户' }}</h1>
          </div>
          <p class="welcome-desc">欢迎使用医药宝，这里是您的个人药品管理中心</p>
        </div>
        <div class="welcome-stats">
          <div class="quick-stat">
            <div class="stat-icon-bg blue">
              <el-icon :size="24"><FirstAidKit /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-num">{{ stats.totalDrugs }}</span>
              <span class="stat-label">我的药品</span>
            </div>
          </div>
        </div>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" size="large" class="action-btn primary" @click="$router.push('/drugs')">
          <el-icon :size="18"><Search /></el-icon>
          <span>浏览药品</span>
        </el-button>
        <el-button size="large" class="action-btn secondary" @click="$router.push('/cabinets')">
          <el-icon :size="18"><Box /></el-icon>
          <span>我的药箱</span>
        </el-button>
      </div>
    </el-card>

    <!-- 过期药品和库存不足警告提示 -->
    <transition name="slide-down">
      <el-alert
        v-if="stats.expired > 0 || stats.expiringSoon > 0 || stats.lowStock > 0"
        :title="alertTitle"
        :type="alertType"
        show-icon
        :closable="false"
        class="expiry-alert"
        @click="$router.push('/cabinets')"
      >
        <template #default>
          <div class="alert-content">
            <span>{{ alertDescription }}</span>
            <el-button 
              :type="alertButtonType" 
              size="small"
              plain
              @click.stop="$router.push('/cabinets')"
            >
              查看详情
            </el-button>
          </div>
        </template>
      </el-alert>
    </transition>

    <!-- 功能卡片 -->
    <el-row :gutter="20" class="feature-row">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/drugs')">
          <div class="feature-content">
            <div class="feature-icon-wrapper blue">
              <el-icon :size="28"><FirstAidKit /></el-icon>
            </div>
            <div class="feature-text">
              <h3>药品浏览</h3>
              <p>查看药品详情、适用症状和使用说明</p>
            </div>
            <el-icon class="feature-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/categories')">
          <div class="feature-content">
            <div class="feature-icon-wrapper green">
              <el-icon :size="28"><Collection /></el-icon>
            </div>
            <div class="feature-text">
              <h3>分类浏览</h3>
              <p>按分类查看药品，快速找到所需类型</p>
            </div>
            <el-icon class="feature-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/cabinets')">
          <div class="feature-content">
            <div class="feature-icon-wrapper orange">
              <el-icon :size="28"><Box /></el-icon>
            </div>
            <div class="feature-text">
              <h3>我的药箱</h3>
              <p>管理个人药箱，跟踪有效期和库存</p>
            </div>
            <el-icon class="feature-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计信息 -->
    <el-card class="stats-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon :size="20" color="#409EFF"><TrendCharts /></el-icon>
            <span>药箱概览</span>
          </div>
          <el-link type="primary" :underline="false" @click="$router.push('/cabinets')">
            查看详情
            <el-icon class="link-arrow"><ArrowRight /></el-icon>
          </el-link>
        </div>
      </template>
      
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6">
          <div class="stat-item">
            <div class="stat-item-icon blue">
              <el-icon :size="24"><FirstAidKit /></el-icon>
            </div>
            <div class="stat-item-content">
              <div class="stat-value">{{ stats.totalDrugs }}</div>
              <div class="stat-label">药品总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-item">
            <div class="stat-item-icon green">
              <el-icon :size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-item-content">
              <div class="stat-value text-success">{{ stats.validDrugs }}</div>
              <div class="stat-label">有效期内</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-item">
            <div class="stat-item-icon warning">
              <el-icon :size="24"><Timer /></el-icon>
            </div>
            <div class="stat-item-content">
              <div class="stat-value text-warning">{{ stats.expiringSoon }}</div>
              <div class="stat-label">即将过期</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-item">
            <div class="stat-item-icon danger">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="stat-item-content">
              <div class="stat-value text-danger">{{ stats.expired }}</div>
              <div class="stat-label">已过期</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-item">
            <div class="stat-item-icon purple">
              <el-icon :size="24"><Box /></el-icon>
            </div>
            <div class="stat-item-content">
              <div class="stat-value" style="color: #8E44AD;">{{ stats.lowStock }}</div>
              <div class="stat-label">库存不足</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { 
  FirstAidKit, 
  Collection, 
  Box, 
  Search, 
  ArrowRight,
  TrendCharts,
  CircleCheck,
  Timer,
  Warning,
  ShoppingCart
} from '@element-plus/icons-vue'

const authStore = useAuthStore()

const stats = ref({
  totalDrugs: 0,
  validDrugs: 0,
  expiringSoon: 0,
  expired: 0,
  lowStock: 0
})

// 问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 警告类型
const alertType = computed(() => {
  if (stats.value.expired > 0) return 'error'
  if (stats.value.expiringSoon > 0) return 'warning'
  return 'info'
})

const alertButtonType = computed(() => {
  if (stats.value.expired > 0) return 'danger'
  if (stats.value.expiringSoon > 0) return 'warning'
  return 'info'
})

// 警告标题
const alertTitle = computed(() => {
  if (stats.value.expired > 0) {
    return `发现 ${stats.value.expired} 个药品已过期`
  } else if (stats.value.expiringSoon > 0) {
    return `有 ${stats.value.expiringSoon} 个药品即将过期`
  } else if (stats.value.lowStock > 0) {
    return `有 ${stats.value.lowStock} 个药品库存不足`
  }
  return ''
})

// 警告描述
const alertDescription = computed(() => {
  const parts = []
  if (stats.value.expired > 0) parts.push(`${stats.value.expired} 个已过期`)
  if (stats.value.expiringSoon > 0) parts.push(`${stats.value.expiringSoon} 个将在7天内过期`)
  if (stats.value.lowStock > 0) parts.push(`${stats.value.lowStock} 个库存不足`)
  
  if (parts.length > 0) {
    return '其中 ' + parts.join('，') + '，请及时处理'
  }
  return ''
})

const fetchStats = async () => {
  try {
    const response = await api.get('/syyb/expiring_drugs/')
    const data = response.data
    stats.value.totalDrugs = data.total_count || 0
    stats.value.validDrugs = data.valid_count || 0
    stats.value.expiringSoon = data.expiring_soon_count || 0
    stats.value.expired = data.expired_count || 0
    
    // 获取库存不足统计
    try {
      const cabinetRes = await api.get('/syyb/cabinets/')
      const cabinets = cabinetRes.data.results || []
      let lowStockCount = 0
      
      for (const cabinet of cabinets) {
        const drugsRes = await api.get(`/syyb/cabinets/${cabinet.id}/drugs/`)
        const drugs = drugsRes.data.results || []
        lowStockCount += drugs.filter((d: any) => d.quantity <= 2).length
      }
      stats.value.lowStock = lowStockCount
    } catch (e) {
      console.error('获取库存统计失败:', e)
    }
  } catch (error) {
      console.error('获取统计失败:', error)
    }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.home-page {
  padding: 0;
}

/* 欢迎卡片 */
.welcome-card {
  margin-bottom: 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  overflow: hidden;
}

.welcome-card :deep(.el-card__body) {
  padding: 32px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.greeting {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.greeting-icon {
  font-size: 32px;
  animation: wave 2s infinite ease-in-out;
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-10deg); }
}

.welcome-text h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.welcome-desc {
  margin: 8px 0 0 0;
  opacity: 0.95;
  font-size: 15px;
  font-weight: 500;
}

.welcome-stats {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 16px 24px;
}

.quick-stat {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon-bg {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
}

.stat-icon-bg.blue {
  color: #409EFF;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.stat-info .stat-label {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  border-radius: 10px;
  padding: 0 24px;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: #fff;
  color: #667eea;
  border: none;
}

.action-btn.primary:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

/* 过期警告 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.expiry-alert {
  margin-bottom: 24px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.expiry-alert:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

/* 功能卡片 */
.feature-row {
  margin-bottom: 24px;
}

.feature-card {
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.feature-card :deep(.el-card__body) {
  padding: 24px;
}

.feature-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.feature-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.feature-icon-wrapper.blue {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.3);
}

.feature-icon-wrapper.green {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
  box-shadow: 0 8px 20px rgba(103, 194, 58, 0.3);
}

.feature-icon-wrapper.orange {
  background: linear-gradient(135deg, #E6A23C 0%, #f3d19e 100%);
  box-shadow: 0 8px 20px rgba(230, 162, 60, 0.3);
}

.feature-text {
  flex: 1;
}

.feature-text h3 {
  margin: 0 0 6px 0;
  font-size: 17px;
  color: #303133;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.feature-text p {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  font-weight: 500;
}

.feature-arrow {
  color: #c0c4cc;
  font-size: 18px;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-arrow {
  color: #409EFF;
  transform: translateX(4px);
}

/* 统计卡片 */
.stats-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.stats-card :deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f2f5;
}

.stats-card :deep(.el-card__body) {
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.link-arrow {
  font-size: 12px;
  margin-left: 4px;
  transition: transform 0.3s ease;
}

.el-link:hover .link-arrow {
  transform: translateX(4px);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #f0f2f5;
  transform: translateY(-2px);
}

.stat-item-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-item-icon.blue {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.stat-item-icon.green {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-item-icon.warning {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.stat-item-icon.danger {
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
}

.stat-item-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #303133;
  line-height: 1;
  margin-bottom: 6px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-value.text-success {
  color: #67C23A;
}

.stat-value.text-warning {
  color: #E6A23C;
}

.stat-value.text-danger {
  color: #F56C6C;
}

.stat-item-content .stat-label {
  font-size: 13px;
  color: #909399;
}

@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .welcome-stats {
    width: 100%;
  }
  
  .welcome-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .stat-item {
    margin-bottom: 12px;
  }
}
</style>
