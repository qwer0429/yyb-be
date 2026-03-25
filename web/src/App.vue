<template>
  <div class="app-wrapper">
    <!-- 登录页单独布局 -->
    <template v-if="isLoginPage">
      <router-view />
    </template>
    
    <!-- 主布局 -->
    <template v-else>
      <el-container class="layout-container">
        <!-- 侧边栏 -->
        <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
          <div class="logo">
            <el-icon :size="28" color="#fff"><FirstAidKit /></el-icon>
            <span v-show="!isCollapse" class="logo-text">医药宝</span>
          </div>
          
          <el-menu
            :default-active="activeMenu"
            :collapse="isCollapse"
            :collapse-transition="false"
            router
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
            class="sidebar-menu"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <template #title>首页</template>
            </el-menu-item>
            
            <el-menu-item index="/drugs">
              <el-icon><FirstAidKit /></el-icon>
              <template #title>药品管理</template>
            </el-menu-item>
            
            <el-menu-item index="/categories">
              <el-icon><Collection /></el-icon>
              <template #title>分类管理</template>
            </el-menu-item>
            
            <el-menu-item index="/manufacturers">
              <el-icon><OfficeBuilding /></el-icon>
              <template #title>厂商管理</template>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-container>
          <!-- 顶部导航栏 -->
          <el-header class="header">
            <div class="header-left">
              <el-icon 
                class="collapse-btn" 
                :size="20"
                @click="toggleCollapse"
              >
                <FoldIcon v-if="!isCollapse" />
                <ExpandIcon v-else />
              </el-icon>
              <breadcrumb />
            </div>
            
            <div class="header-right">
              <!-- 全屏按钮 -->
              <el-tooltip content="全屏" placement="bottom">
                <el-icon class="header-icon" :size="18" @click="toggleFullscreen">
                  <FullScreen />
                </el-icon>
              </el-tooltip>
              
              <!-- 用户菜单 -->
              <el-dropdown @command="handleCommand">
                <div class="user-info">
                  <el-avatar :size="32" :icon="UserFilled" />
                  <span class="username">{{ authStore.username || '管理员' }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>个人中心
                    </el-dropdown-item>
                    <el-dropdown-item command="settings">
                      <el-icon><Setting /></el-icon>系统设置
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-header>
          
          <!-- 主内容区 -->
          <el-main class="main-content">
            <router-view v-slot="{ Component }">
              <transition name="fade-transform" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </el-main>
        </el-container>
      </el-container>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { ElMessageBox } from 'element-plus';
import { 
  FirstAidKit, 
  HomeFilled, 
  Collection, 
  OfficeBuilding, 
  Fold as FoldIcon, 
  Expand as ExpandIcon, 
  FullScreen, 
  UserFilled, 
  ArrowDown, 
  User, 
  Setting, 
  SwitchButton 
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isCollapse = ref(false);

const isLoginPage = computed(() => route.path === '/login');
const activeMenu = computed(() => route.path);

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
};

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile');
      break;
    case 'settings':
      router.push('/settings');
      break;
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        authStore.logout();
        router.push('/login');
      });
      break;
  }
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-wrapper {
  height: 100%;
}

.layout-container {
  height: 100vh;
}

/* 侧边栏样式 */
.sidebar {
  background-color: #304156;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3649;
  border-bottom: 1px solid #1f2d3d;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin-left: 12px;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #263445 !important;
}

/* 顶部栏样式 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.collapse-btn {
  cursor: pointer;
  color: #606266;
  padding: 10px;
  border-radius: 4px;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background-color: #f5f7fa;
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  cursor: pointer;
  color: #606266;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.header-icon:hover {
  background-color: #f5f7fa;
  color: #409EFF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #606266;
}

/* 主内容区样式 */
.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

/* Chrome/Safari 隐藏滚动条 */
.main-content::-webkit-scrollbar {
  display: none;
}

/* 页面切换动画 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Element Plus 样式覆盖 */
:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
