<template>
  <div class="register-container">
    <!-- 动态背景 -->
    <div class="animated-bg">
      <div class="bg-bubble" v-for="n in 6" :key="n"></div>
    </div>
    
    <div class="register-box" :class="{ 'box-appear': mounted }">
      <div class="register-header">
        <div class="logo-wrapper">
          <el-icon :size="48" class="logo-icon"><FirstAidKit /></el-icon>
        </div>
        <h1>创建账号</h1>
        <p class="subtitle">加入医药宝，管理您的健康</p>
      </div>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
            class="animated-input"
          />
        </el-form-item>
        
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item prop="name">
              <el-input
                v-model="registerForm.name"
                placeholder="真实姓名（可选）"
                size="large"
                :prefix-icon="UserFilled"
                clearable
                class="animated-input"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="mobile">
              <el-input
                v-model="registerForm.mobile"
                placeholder="手机号（可选）"
                size="large"
                :prefix-icon="Phone"
                clearable
                class="animated-input"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
            class="animated-input"
          />
          <div class="password-hint">
            <p>密码要求：8-20位，包含大小写字母、数字和特殊字符</p>
          </div>
        </el-form-item>
        
        <el-form-item prop="password_confirm">
          <el-input
            v-model="registerForm.password_confirm"
            type="password"
            placeholder="请确认密码"
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
            class="register-button"
            :loading="authStore.isLoading"
            :class="{ 'btn-pulse': !authStore.isLoading }"
            @click="handleRegister"
          >
            <span class="btn-text">创建账号</span>
            <el-icon class="btn-icon"><ArrowRight /></el-icon>
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-footer">
        <p class="login-tip">
          已有账号？
          <router-link to="/login" class="login-link">
            立即登录
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
import { User, UserFilled, Lock, Phone, ArrowRight } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const registerFormRef = ref<FormInstance>()
const mounted = ref(false)

onMounted(() => {
  setTimeout(() => {
    mounted.value = true
  }, 100)
})

const registerForm = reactive({
  username: '',
  name: '',
  mobile: '',
  password: '',
  password_confirm: ''
})

// 自定义验证：强密码规则
const validateStrongPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
    return
  }
  if (value.length < 8 || value.length > 20) {
    callback(new Error('密码长度需在 8-20 位之间'))
    return
  }
  if (!/[A-Z]/.test(value)) {
    callback(new Error('密码需包含至少一个大写字母'))
    return
  }
  if (!/[a-z]/.test(value)) {
    callback(new Error('密码需包含至少一个小写字母'))
    return
  }
  if (!/\d/.test(value)) {
    callback(new Error('密码需包含至少一个数字'))
    return
  }
  if (!/[!@#$%^&*(),.?":{}|<>_+\-=\[\];'\\/]/.test(value)) {
    callback(new Error('密码需包含至少一个特殊字符'))
    return
  }
  callback()
}

// 自定义验证：确认密码
const validatePassConfirm = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 自定义验证：手机号
const validateMobile = (rule: any, value: any, callback: any) => {
  if (value === '' || value === undefined) {
    callback() // 手机号可选
  } else {
    const mobileRegex = /^1[3-9]\d{9}$/
    if (!mobileRegex.test(value)) {
      callback(new Error('请输入正确的手机号'))
    } else {
      callback()
    }
  }
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  name: [
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  mobile: [
    { validator: validateMobile, trigger: 'blur' }
  ],
  password: [
    { required: true, trigger: 'blur' },
    { validator: validateStrongPassword, trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePassConfirm, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await authStore.register({
        username: registerForm.username,
        password: registerForm.password,
        password_confirm: registerForm.password_confirm,
        mobile: registerForm.mobile || undefined,
        name: registerForm.name || undefined
      })
      if (success) {
        router.push('/')
      }
    }
  })
}
</script>

<style scoped>
.register-container {
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

.register-box {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 40px 48px;
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

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-wrapper {
  width: 88px;
  height: 88px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(103, 194, 58, 0.3);
  animation: logo-pulse 2s infinite ease-in-out;
}

@keyframes logo-pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 10px 30px rgba(103, 194, 58, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 15px 40px rgba(103, 194, 58, 0.4);
  }
}

.logo-icon {
  color: #fff;
}

.register-header h1 {
  font-size: 28px;
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

.register-form {
  margin-top: 24px;
}

.password-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.password-hint p {
  margin: 0;
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
  box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08);
}

.animated-input :deep(.el-input__inner) {
  height: 48px;
  font-size: 15px;
}

.register-button {
  width: 100%;
  height: 52px;
  font-size: 17px;
  font-weight: 600;
  border-radius: 12px;
  margin-top: 8px;
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
  border: none;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.register-button:hover {
  background: linear-gradient(135deg, #85ce61 0%, #b3e19d 100%);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(103, 194, 58, 0.4);
}

.register-button:active {
  transform: translateY(0);
}

.btn-pulse {
  animation: btn-glow 2s infinite ease-in-out;
}

@keyframes btn-glow {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(103, 194, 58, 0.3);
  }
  50% {
    box-shadow: 0 8px 25px rgba(103, 194, 58, 0.5);
  }
}

.btn-text {
  position: relative;
  z-index: 1;
}

.btn-icon {
  transition: transform 0.3s ease;
}

.register-button:hover .btn-icon {
  transform: translateX(4px);
}

.register-footer {
  text-align: center;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.login-tip {
  color: #606266;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.login-link {
  color: #67C23A;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.login-link:hover {
  color: #85ce61;
  gap: 8px;
}

.link-icon {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.login-link:hover .link-icon {
  transform: translateX(4px);
}

.copyright {
  color: #c0c4cc;
  font-size: 12px;
  margin: 0;
}

@media (max-width: 480px) {
  .register-box {
    padding: 32px 24px;
    border-radius: 20px;
  }
  
  .register-header h1 {
    font-size: 24px;
  }
  
  .logo-wrapper {
    width: 72px;
    height: 72px;
  }
}
</style>
