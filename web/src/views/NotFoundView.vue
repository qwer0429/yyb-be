<template>
  <div class="not-found">
    <div class="content">
      <h1>404</h1>
      <h2>页面未找到</h2>
      <p>抱歉，您访问的页面不存在或已被移除</p>
      <el-button type="primary" size="large" @click="$router.push('/')">
        <el-icon><HomeFilled /></el-icon>
        返回首页
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: calc(100vh - 100px);
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.content h1 {
  font-size: 120px;
  font-weight: 700;
  color: #409EFF;
  margin: 0;
  line-height: 1;
}

.content h2 {
  font-size: 28px;
  color: #303133;
  margin: 20px 0;
}

.content p {
  font-size: 16px;
  color: #909399;
  margin-bottom: 30px;
}

.content .el-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
</style>
