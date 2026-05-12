<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="animated-bg">
      <div class="bg-bubble" v-for="n in 6" :key="n"></div>
    </div>
    
    <div class="login-box" :class="{ 'box-appear': mounted }">
      <div class="login-header">
        <div class="logo-wrapper">
          <el-icon :size="48" class="logo-icon"><FirstAidKit /></el-icon>
        </div>
        <h1>医药宝</h1>
        <p class="subtitle">用户端系统</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
            class="animated-input"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
            class="animated-input"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="authStore.isLoading"
            :class="{ 'btn-pulse': !authStore.isLoading }"
            @click="handleLogin"
          >
            <span class="btn-text">登 录</span>
            <el-icon class="btn-icon"><ArrowRight /></el-icon>
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p class="register-tip">
          还没有账号？
          <router-link to="/register" class="register-link">
            立即注册
            <el-icon class="link-icon"><ArrowRight /></el-icon>
          </router-link>
        </p>
        <p class="copyright">© 医药宝 - 用户端系统</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, ArrowRight } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref<FormInstance>()
const mounted = ref(false)

onMounted(() => {
  setTimeout(() => {
    mounted.value = true
  }, 100)
})

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await authStore.login(loginForm.username, loginForm.password)
      if (success) {
        // 如果是管理员，直接跳转到后台管理系统（单点登录）
        if (authStore.isAdmin) {
          const adminUrl = import.meta.env.VITE_ADMIN_URL || 'http://192.168.50.82:5173'
          const token = authStore.accessToken
          // 构造带 token 的后台地址，后台会自动完成登录
          window.location.href = `${adminUrl}?portal_token=${token}&from=portal`
        } else {
          // 普通用户进入用户端首页
          router.push('/')
        }
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 动态背景 */
.animated-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.bg-bubble {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 15s infinite ease-in-out;
}

.bg-bubble:nth-child(1) {
  width: 80px;
  height: 80px;
  left: 10%;
  top: 20%;
  animation-delay: 0s;
}

.bg-bubble:nth-child(2) {
  width: 120px;
  height: 120px;
  right: 15%;
  top: 30%;
  animation-delay: 2s;
}

.bg-bubble:nth-child(3) {
  width: 60px;
  height: 60px;
  left: 20%;
  bottom: 20%;
  animation-delay: 4s;
}

.bg-bubble:nth-child(4) {
  width: 100px;
  height: 100px;
  right: 20%;
  bottom: 30%;
  animation-delay: 6s;
}

.bg-bubble:nth-child(5) {
  width: 70px;
  height: 70px;
  left: 50%;
  top: 10%;
  animation-delay: 8s;
}

.bg-bubble:nth-child(6) {
  width: 90px;
  height: 90px;
  right: 10%;
  bottom: 10%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 0.6;
  }
}

.login-box {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  z-index: 1;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.box-appear {
  opacity: 1;
  transform: translateY(0);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-wrapper {
  width: 88px;
  height: 88px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(64, 158, 255, 0.3);
  animation: logo-pulse 2s infinite ease-in-out;
}

@keyframes logo-pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 10px 30px rgba(64, 158, 255, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 15px 40px rgba(64, 158, 255, 0.4);
  }
}

.logo-icon {
  color: #fff;
}

.login-header h1 {
  font-size: 32px;
  color: #303133;
  margin: 0 0 8px 0;
  font-weight: 700;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  color: #606266;
  font-size: 15px;
  margin: 0;
  font-weight: 500;
}

.login-form {
  margin-top: 32px;
}

.animated-input :deep(.el-input__wrapper) {
  padding: 4px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.animated-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.animated-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08);
}

.animated-input :deep(.el-input__inner) {
  height: 48px;
  font-size: 15px;
}

.login-button {
  width: 100%;
  height: 52px;
  font-size: 17px;
  font-weight: 600;
  border-radius: 12px;
  margin-top: 8px;
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
  border: none;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-button:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #95d475 100%);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(64, 158, 255, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.btn-pulse {
  animation: btn-glow 2s infinite ease-in-out;
}

@keyframes btn-glow {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
  }
  50% {
    box-shadow: 0 8px 25px rgba(64, 158, 255, 0.5);
  }
}

.btn-text {
  position: relative;
  z-index: 1;
}

.btn-icon {
  transition: transform 0.3s ease;
}

.login-button:hover .btn-icon {
  transform: translateX(4px);
}

.login-footer {
  text-align: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.register-tip {
  color: #606266;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.register-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.register-link:hover {
  color: #66b1ff;
  gap: 8px;
}

.link-icon {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.register-link:hover .link-icon {
  transform: translateX(4px);
}

.copyright {
  color: #c0c4cc;
  font-size: 12px;
  margin: 0;
}

@media (max-width: 480px) {
  .login-box {
    padding: 36px 24px;
    border-radius: 20px;
  }
  
  .login-header h1 {
    font-size: 28px;
  }
  
  .logo-wrapper {
    width: 72px;
    height: 72px;
  }
}
</style>
