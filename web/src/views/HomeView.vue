<template>
  <div class="home-page">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card" shadow="never">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎使用医药宝管理系统</h1>
          <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
        </div>
        <el-icon class="welcome-icon" :size="80" color="#409EFF"><First-Aid-Kit /></el-icon>
      </div>
    </el-card>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon blue">
              <el-icon :size="32"><First-Aid-Kit /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.drugCount }}</p>
              <p class="stat-label">药品总数</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon green">
              <el-icon :size="32"><Collection /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.categoryCount }}</p>
              <p class="stat-label">分类数量</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon orange">
              <el-icon :size="32"><Office-Building /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.manufacturerCount }}</p>
              <p class="stat-label">厂商数量</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon purple">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.userCount }}</p>
              <p class="stat-label">用户数量</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快捷操作和热门药品 -->
    <el-row :gutter="20" class="main-row">
      <el-col :span="12">
        <el-card title="快捷操作" shadow="never">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="$router.push('/drugs')">
              <div class="action-icon blue">
                <el-icon :size="24"><First-Aid-Kit /></el-icon>
              </div>
              <span>药品管理</span>
            </div>
            <div class="action-item" @click="$router.push('/categories')">
              <div class="action-icon green">
                <el-icon :size="24"><Collection /></el-icon>
              </div>
              <span>分类管理</span>
            </div>
            <div class="action-item" @click="$router.push('/manufacturers')">
              <div class="action-icon orange">
                <el-icon :size="24"><Office-Building /></el-icon>
              </div>
              <span>厂商管理</span>
            </div>
            <div class="action-item" @click="handleSearch">
              <div class="action-icon purple">
                <el-icon :size="24"><Search /></el-icon>
              </div>
              <span>药品搜索</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>热门药品</span>
              <el-link type="primary" @click="$router.push('/drugs')">查看更多</el-link>
            </div>
          </template>
          <el-table :data="hotDrugs" stripe style="width: 100%">
            <el-table-column prop="trade_name" label="商品名" show-overflow-tooltip />
            <el-table-column prop="drug_name" label="通用名" show-overflow-tooltip />
            <el-table-column prop="manufacturer_name" label="厂商" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '../api';
import { ElMessage } from 'element-plus';

// 当前日期
const currentDate = computed(() => {
  const date = new Date();
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${weekdays[date.getDay()]}`;
});

// 统计数据
const stats = ref({
  drugCount: 0,
  categoryCount: 0,
  manufacturerCount: 0,
  userCount: 0
});

// 热门药品
const hotDrugs = ref([]);

// 获取统计数据
const fetchStats = async () => {
  try {
    const [drugRes, type1Res, type2Res, holderRes, mfrRes] = await Promise.all([
      api.get('/syyb/drug/'),
      api.get('/syyb/type1drug/'),
      api.get('/syyb/type2drug/'),
      api.get('/syyb/manufacturerholder/'),
      api.get('/syyb/manufacturer/')
    ]);
    
    stats.value.drugCount = drugRes.data.count || 0;
    stats.value.categoryCount = (type1Res.data.count || 0) + (type2Res.data.count || 0);
    stats.value.manufacturerCount = (holderRes.data.count || 0) + (mfrRes.data.count || 0);
    stats.value.userCount = 1; // 暂时固定
    
    // 获取热门药品（前5个）
    const drugs = drugRes.data.results || [];
    hotDrugs.value = drugs.filter((d: any) => d.is_hot).slice(0, 5);
    
    // 如果没有热门标记的，取前5个
    if (hotDrugs.value.length === 0) {
      hotDrugs.value = drugs.slice(0, 5);
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

const handleSearch = () => {
  ElMessage.info('搜索功能请前往药品管理页面');
};

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.home-page {
  padding: 0;
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: none;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
}

.welcome-text h1 {
  font-size: 28px;
  color: #1976d2;
  margin: 0 0 10px 0;
}

.welcome-text p {
  font-size: 16px;
  color: #546e7a;
  margin: 0;
}

.welcome-icon {
  opacity: 0.8;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #E6A23C 0%, #f3d19e 100%);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #8E44AD 0%, #bb8fce 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 5px 0 0 0;
}

.main-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #f5f7fa;
}

.action-item:hover {
  background: #e4e7ed;
  transform: translateX(5px);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.action-icon.blue {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
}

.action-icon.green {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
}

.action-icon.orange {
  background: linear-gradient(135deg, #E6A23C 0%, #f3d19e 100%);
}

.action-icon.purple {
  background: linear-gradient(135deg, #8E44AD 0%, #bb8fce 100%);
}

.action-item span {
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}
</style>
