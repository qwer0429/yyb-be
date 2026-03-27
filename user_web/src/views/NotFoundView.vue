<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-illustration">
        <div class="planet"></div>
        <div class="astronaut">🚀</div>
        <div class="stars">
          <span v-for="n in 20" :key="n" class="star"></span>
        </div>
      </div>
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面迷失在太空了</h2>
      <p class="error-desc">抱歉，您访问的页面不存在或已被移动到其他地方</p>
      <div class="error-actions">
        <el-button type="primary" size="large" class="home-btn" @click="$router.push('/')">
          <el-icon><HomeFilled /></el-icon>
          <span>返回首页</span>
        </el-button>
        <el-button size="large" class="back-btn" @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回上一页</span>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { HomeFilled, ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1f3c 0%, #2d3561 50%, #667eea 100%);
  position: relative;
  overflow: hidden;
}

.not-found-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.not-found-content {
  text-align: center;
  position: relative;
  z-index: 1;
  padding: 40px;
}

/* 插图动画 */
.error-illustration {
  width: 200px;
  height: 200px;
  margin: 0 auto 40px;
  position: relative;
}

.planet {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 50%, #a0cfff 100%);
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 
    0 0 60px rgba(64, 158, 255, 0.4),
    inset -20px -20px 40px rgba(0, 0, 0, 0.1);
  animation: planet-float 4s infinite ease-in-out;
}

.planet::before {
  content: '';
  position: absolute;
  top: 30%;
  left: 20%;
  width: 30px;
  height: 15px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: rotate(-20deg);
}

@keyframes planet-float {
  0%, 100% {
    transform: translate(-50%, -50%) translateY(0);
  }
  50% {
    transform: translate(-50%, -50%) translateY(-10px);
  }
}

.astronaut {
  font-size: 48px;
  position: absolute;
  top: 10%;
  right: 10%;
  animation: astronaut-float 3s infinite ease-in-out;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.2));
}

@keyframes astronaut-float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-15px) rotate(10deg);
  }
}

/* 星星 */
.stars {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.star {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #fff;
  border-radius: 50%;
  animation: twinkle 2s infinite ease-in-out;
}

.star:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
.star:nth-child(2) { top: 20%; left: 80%; animation-delay: 0.2s; }
.star:nth-child(3) { top: 60%; left: 5%; animation-delay: 0.4s; }
.star:nth-child(4) { top: 80%; left: 70%; animation-delay: 0.6s; }
.star:nth-child(5) { top: 30%; left: 50%; animation-delay: 0.8s; }
.star:nth-child(6) { top: 70%; left: 30%; animation-delay: 1s; }
.star:nth-child(7) { top: 15%; left: 60%; animation-delay: 1.2s; }
.star:nth-child(8) { top: 85%; left: 15%; animation-delay: 1.4s; }
.star:nth-child(9) { top: 45%; left: 90%; animation-delay: 1.6s; }
.star:nth-child(10) { top: 5%; left: 40%; animation-delay: 1.8s; }
.star:nth-child(11) { top: 55%; left: 25%; animation-delay: 0.1s; }
.star:nth-child(12) { top: 35%; left: 75%; animation-delay: 0.3s; }
.star:nth-child(13) { top: 75%; left: 55%; animation-delay: 0.5s; }
.star:nth-child(14) { top: 25%; left: 15%; animation-delay: 0.7s; }
.star:nth-child(15) { top: 65%; left: 85%; animation-delay: 0.9s; }
.star:nth-child(16) { top: 90%; left: 45%; animation-delay: 1.1s; }
.star:nth-child(17) { top: 40%; left: 35%; animation-delay: 1.3s; }
.star:nth-child(18) { top: 8%; left: 95%; animation-delay: 1.5s; }
.star:nth-child(19) { top: 95%; left: 5%; animation-delay: 1.7s; }
.star:nth-child(20) { top: 50%; left: 50%; animation-delay: 1.9s; }

@keyframes twinkle {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

/* 错误信息 */
.error-code {
  font-size: 120px;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, #a0cfff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
  line-height: 1;
  text-shadow: 0 10px 30px rgba(64, 158, 255, 0.3);
}

.error-title {
  font-size: 32px;
  color: #fff;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.error-desc {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 40px 0;
}

/* 按钮 */
.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.home-btn {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
  border: none;
  padding: 0 32px;
  height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 12px;
  font-weight: 600;
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(64, 158, 255, 0.4);
}

.back-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 0 32px;
  height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

@media (max-width: 480px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-title {
    font-size: 24px;
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .error-illustration {
    width: 150px;
    height: 150px;
  }
  
  .planet {
    width: 90px;
    height: 90px;
  }
  
  .astronaut {
    font-size: 36px;
  }
}
</style>
