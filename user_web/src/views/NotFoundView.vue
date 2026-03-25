<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <el-icon :size="120" color="#409EFF"><Warning /></el-icon>
      <h1>404</h1>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" size="large" @click="$router.push('/')">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Warning } from '@element-plus/icons-vue'
</script>

<style scoped>
.not-found-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.not-found-content {
  text-align: center;
}

.not-found-content h1 {
  font-size: 72px;
  color: #303133;
  margin: 20px 0;
  font-weight: 700;
}

.not-found-content p {
  font-size: 18px;
  color: #909399;
  margin-bottom: 30px;
}
</style>
