<template>
  <div class="home-page">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="never">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎使用医药宝用户端 👋</h1>
          <p>在这里您可以浏览药品信息、查看分类、管理您的个人药箱</p>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="$router.push('/drugs')">
            <el-icon><FirstAidKit /></el-icon>
            浏览药品
          </el-button>
          <el-button type="success" size="large" @click="$router.push('/cabinets')">
            <el-icon><Box /></el-icon>
            我的药箱
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 功能卡片 -->
    <el-row :gutter="20" class="feature-row">
      <el-col :span="8">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/drugs')">
          <div class="feature-icon blue">
            <el-icon :size="32"><FirstAidKit /></el-icon>
          </div>
          <h3>药品浏览</h3>
          <p>查看所有药品信息，了解药品详情、适用症状和使用说明</p>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/categories')">
          <div class="feature-icon green">
            <el-icon :size="32"><Collection /></el-icon>
          </div>
          <h3>分类浏览</h3>
          <p>按分类查看药品，快速找到您需要的药品类型</p>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card" shadow="hover" @click="$router.push('/cabinets')">
          <div class="feature-icon orange">
            <el-icon :size="32"><Box /></el-icon>
          </div>
          <h3>我的药箱</h3>
          <p>管理您的个人药箱，跟踪药品有效期和库存情况</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 统计信息 -->
    <el-card class="stats-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>药箱概览</span>
          <el-link type="primary" @click="$router.push('/cabinets')">查看详情</el-link>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalDrugs }}</div>
            <div class="stat-label">药品总数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value text-success">{{ stats.validDrugs }}</div>
            <div class="stat-label">有效期内</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value text-warning">{{ stats.expiringSoon }}</div>
            <div class="stat-label">即将过期</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value text-danger">{{ stats.expired }}</div>
            <div class="stat-label">已过期</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 快捷操作 -->
    <el-card class="quick-actions" shadow="never">
      <template #header>
        <span>快捷操作</span>
      </template>
      
      <div class="action-list">
        <div class="action-item" @click="$router.push('/drugs')">
          <el-icon :size="20" color="#409EFF"><Search /></el-icon>
          <span>搜索药品</span>
        </div>
        <div class="action-item" @click="$router.push('/categories')">
          <el-icon :size="20" color="#67C23A"><FolderOpened /></el-icon>
          <span>浏览分类</span>
        </div>
        <div class="action-item" @click="$router.push('/cabinets')">
          <el-icon :size="20" color="#E6A23C"><Plus /></el-icon>
          <span>添加药品到药箱</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api'
import { FirstAidKit, Collection, Box, Search, FolderOpened, Plus } from '@element-plus/icons-vue'

const stats = ref({
  totalDrugs: 0,
  validDrugs: 0,
  expiringSoon: 0,
  expired: 0
})

const fetchStats = async () => {
  try {
    const response = await api.get('/syyb/expiring_drugs/')
    const data = response.data
    stats.value.totalDrugs = data.total_count || 0
    stats.value.validDrugs = data.valid_count || 0
    stats.value.expiringSoon = data.expiring_soon_count || 0
    stats.value.expired = data.expired_count || 0
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

.welcome-card {
  margin-bottom: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.welcome-text h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.welcome-text p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

.feature-row {
  margin-bottom: 20px;
}

.feature-card {
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
  padding: 20px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #fff;
}

.feature-icon.blue {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
}

.feature-icon.green {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
}

.feature-icon.orange {
  background: linear-gradient(135deg, #E6A23C 0%, #f3d19e 100%);
}

.feature-card h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

.stats-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
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

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  border-radius: 12px;
}

.action-list {
  display: flex;
  gap: 20px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: #e6f2ff;
}
</style>
