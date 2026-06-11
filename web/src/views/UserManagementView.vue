<template>
  <div class="user-management-page">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon blue">
              <el-icon :size="24"><User /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ statistics.total }}</p>
              <p class="stat-label">用户总数</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon orange">
              <el-icon :size="24"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ statistics.admin_count }}</p>
              <p class="stat-label">管理员</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon green">
              <el-icon :size="24"><Avatar /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ statistics.user_count }}</p>
              <p class="stat-label">普通用户</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon success">
              <el-icon :size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ statistics.active_count }}</p>
              <p class="stat-label">已启用</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon danger">
              <el-icon :size="24"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ statistics.inactive_count }}</p>
              <p class="stat-label">已禁用</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-item">
            <div class="stat-icon purple">
              <el-icon :size="24"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ statistics.today_count }}</p>
              <p class="stat-label">今日新增</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和操作栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="用户名/姓名/手机号"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="全部角色" clearable style="width: 120px">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="已启用" value="true" />
            <el-option label="已禁用" value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="operation-bar">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>新增用户
        </el-button>
        <el-button type="danger" :disabled="!selectedUsers.length" @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>批量删除({{ selectedUsers.length }})
        </el-button>
      </div>
    </el-card>

    <!-- 用户表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="users"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="40" :icon="UserFilled" />
              <div class="user-info">
                <span class="user-name">{{ row.name || row.username }}</span>
                <span class="user-username">@{{ row.username }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="手机号" prop="mobile" width="130">
          <template #default="{ row }">
            <span>{{ row.mobile || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="邮箱" prop="email" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.email || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="性别" width="80">
          <template #default="{ row }">
            <span>{{ row.sex_display || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'success'" size="small">
              {{ row.is_admin ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="注册时间" prop="date_joined" width="160">
          <template #default="{ row }">
            <span>{{ formatDate(row.date_joined) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="最后登录" prop="last_login" width="160">
          <template #default="{ row }">
            <span>{{ row.last_login ? formatDate(row.last_login) : '从未登录' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="warning" text size="small" @click="handleResetPassword(row)">
              <el-icon><Key /></el-icon>重置密码
            </el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="550px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="userForm"
        :rules="userRules"
        label-width="90px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码（默认123456）" />
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model="userForm.mobile" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="性别" prop="sex">
          <el-radio-group v-model="userForm.sex">
            <el-radio :label="1">男</el-radio>
            <el-radio :label="2">女</el-radio>
            <el-radio :label="3">保密</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="角色" prop="is_admin">
          <el-radio-group v-model="userForm.is_admin">
            <el-radio :label="false">普通用户</el-radio>
            <el-radio :label="true">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  User, UserFilled, Avatar, Search, Plus, Delete, Edit, Key,
  CircleCheck, CircleClose, TrendCharts
} from '@element-plus/icons-vue';

// 搜索表单
const searchForm = reactive({
  search: '',
  role: '',
  is_active: ''
});

// 统计数据
const statistics = reactive({
  total: 0,
  admin_count: 0,
  user_count: 0,
  active_count: 0,
  inactive_count: 0,
  today_count: 0
});

// 表格数据
const loading = ref(false);
const users = ref([]);
const selectedUsers = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 对话框
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const formRef = ref();

// 用户表单
const userForm = reactive({
  id: null,
  username: '',
  password: '',
  name: '',
  mobile: '',
  email: '',
  sex: 1,
  is_admin: false,
  is_active: true
});

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: !isEdit.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
};

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const res = await api.get('/susers/users/statistics/');
    Object.assign(statistics, res.data);
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchForm.search,
      role: searchForm.role,
      is_active: searchForm.is_active
    };
    const res = await api.get('/susers/users/', { params });
    users.value = res.data.results || [];
    total.value = res.data.count || 0;
  } catch (error) {
    ElMessage.error('获取用户列表失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  currentPage.value = 1;
  fetchUsers();
};

// 重置搜索
const handleReset = () => {
  searchForm.search = '';
  searchForm.role = '';
  searchForm.is_active = '';
  handleSearch();
};

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedUsers.value = selection;
};

// 打开新增对话框
const handleAdd = () => {
  isEdit.value = false;
  Object.assign(userForm, {
    id: null,
    username: '',
    password: '',
    name: '',
    mobile: '',
    email: '',
    sex: 1,
    is_admin: false,
    is_active: true
  });
  dialogVisible.value = true;
};

// 打开编辑对话框
const handleEdit = (row: any) => {
  isEdit.value = true;
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    name: row.name,
    mobile: row.mobile,
    email: row.email,
    sex: row.sex || 1,
    is_admin: row.is_admin,
    is_active: row.is_active
  });
  dialogVisible.value = true;
};

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  
  submitting.value = true;
  try {
    if (isEdit.value) {
      await api.put(`/susers/users/${userForm.id}/`, userForm);
      ElMessage.success('更新成功');
    } else {
      await api.post('/susers/users/', userForm);
      ElMessage.success('创建成功');
    }
    dialogVisible.value = false;
    fetchUsers();
    fetchStatistics();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '操作失败');
  } finally {
    submitting.value = false;
  }
};

// 删除用户
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', {
      type: 'warning'
    });
    await api.delete(`/susers/users/${row.id}/`);
    ElMessage.success('删除成功');
    fetchUsers();
    fetchStatistics();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '删除失败');
    }
  }
};

// 批量删除
const handleBatchDelete = async () => {
  const ids = selectedUsers.value.map((u: any) => u.id);
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 个用户吗？`, '提示', {
      type: 'warning'
    });
    await api.delete('/susers/users/batch_delete/', { data: { user_ids: ids } });
    ElMessage.success('批量删除成功');
    fetchUsers();
    fetchStatistics();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '批量删除失败');
    }
  }
};

// 重置密码
const handleResetPassword = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要重置 "${row.username}" 的密码为 "123456" 吗？`, '提示', {
      type: 'warning'
    });
    await api.post(`/susers/users/${row.id}/reset_password/`, { password: '123456' });
    ElMessage.success('密码重置成功');
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '重置密码失败');
    }
  }
};

// 切换用户状态
const handleStatusChange = async (row: any, val: boolean) => {
  try {
    await api.post(`/susers/users/${row.id}/toggle_status/`);
    ElMessage.success(`用户已${val ? '启用' : '禁用'}`);
  } catch (error: any) {
    row.is_active = !val;
    ElMessage.error(error.response?.data?.error || '操作失败');
  }
};

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  fetchUsers();
};

const handlePageChange = (val: number) => {
  currentPage.value = val;
  fetchUsers();
};

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-';
  const d = new Date(date);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

onMounted(() => {
  fetchUsers();
  fetchStatistics();
});
</script>

<style scoped>
.user-management-page {
  padding: 0;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #E6A23C 0%, #f3d19e 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
}

.stat-icon.success {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
}

.stat-icon.danger {
  background: linear-gradient(135deg, #F56C6C 0%, #fab6b6 100%);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #8E44AD 0%, #bb8fce 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin: 4px 0 0 0;
}

/* 搜索卡片 */
.search-card {
  margin-bottom: 20px;
}

.operation-bar {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

/* 用户表格 */
.table-card {
  margin-bottom: 20px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 500;
  color: #303133;
}

.user-username {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
