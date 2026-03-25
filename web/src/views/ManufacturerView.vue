<template>
  <div class="manufacturer-page">
    <el-row :gutter="24">
      <!-- 上市许可持有人 -->
      <el-col :span="12">
        <el-card shadow="hover" class="manufacturer-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <div class="icon-wrapper blue">
                  <el-icon :size="20"><OfficeBuilding /></el-icon>
                </div>
                <div class="title-content">
                  <span class="title-text">上市许可持有人</span>
                  <span class="subtitle">Marketing Authorization Holder</span>
                </div>
                <el-tag type="info" size="small" class="count-tag">{{ holderList.length }}</el-tag>
              </div>
              <el-button type="primary" @click="handleAddHolder" class="add-btn">
                <el-icon><Plus /></el-icon>新增
              </el-button>
            </div>
          </template>
          
          <div v-loading="loading1" class="table-container">
            <el-table 
              :data="holderList" 
              stripe 
              class="custom-table"
              :header-cell-style="{ background: '#f5f7fa', fontWeight: 600 }"
            >
              <el-table-column prop="id" label="ID" width="60" align="center">
                <template #default="{ row }">
                  <span class="id-badge">{{ row.id }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="name" label="全称" min-width="140" show-overflow-tooltip />
              <el-table-column prop="abbreviation" label="简称" width="80" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.abbreviation" type="primary" size="small" effect="plain">
                    {{ row.abbreviation }}
                  </el-tag>
                  <span v-else class="empty-text">-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <div class="action-group">
                    <el-button 
                      type="primary" 
                      text
                      size="small"
                      @click="handleEditHolder(row)"
                    >
                      <el-icon><Edit /></el-icon>编辑
                    </el-button>
                    <el-button 
                      type="danger" 
                      text
                      size="small"
                      @click="handleDeleteHolder(row)"
                    >
                      <el-icon><Delete /></el-icon>删除
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            
            <el-empty v-if="!loading1 && holderList.length === 0" description="暂无数据">
              <el-button type="primary" @click="handleAddHolder">
                <el-icon><Plus /></el-icon>添加持有人
              </el-button>
            </el-empty>
          </div>
        </el-card>
      </el-col>
      
      <!-- 生产厂商 -->
      <el-col :span="12">
        <el-card shadow="hover" class="manufacturer-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <div class="icon-wrapper green">
                  <el-icon :size="20"><Factory /></el-icon>
                </div>
                <div class="title-content">
                  <span class="title-text">生产厂商</span>
                  <span class="subtitle">Manufacturer</span>
                </div>
                <el-tag type="info" size="small" class="count-tag">{{ manufacturerList.length }}</el-tag>
              </div>
              <el-button type="success" @click="handleAddManufacturer" class="add-btn">
                <el-icon><Plus /></el-icon>新增
              </el-button>
            </div>
          </template>
          
          <div v-loading="loading2" class="table-container">
            <el-table 
              :data="manufacturerList" 
              stripe 
              class="custom-table"
              :header-cell-style="{ background: '#f5f7fa', fontWeight: 600 }"
            >
              <el-table-column prop="id" label="ID" width="60" align="center">
                <template #default="{ row }">
                  <span class="id-badge">{{ row.id }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="name" label="全称" min-width="140" show-overflow-tooltip />
              <el-table-column prop="abbreviation" label="简称" width="80" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.abbreviation" type="success" size="small" effect="plain">
                    {{ row.abbreviation }}
                  </el-tag>
                  <span v-else class="empty-text">-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <div class="action-group">
                    <el-button 
                      type="primary" 
                      text
                      size="small"
                      @click="handleEditManufacturer(row)"
                    >
                      <el-icon><Edit /></el-icon>编辑
                    </el-button>
                    <el-button 
                      type="danger" 
                      text
                      size="small"
                      @click="handleDeleteManufacturer(row)"
                    >
                      <el-icon><Delete /></el-icon>删除
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            
            <el-empty v-if="!loading2 && manufacturerList.length === 0" description="暂无数据">
              <el-button type="success" @click="handleAddManufacturer">
                <el-icon><Plus /></el-icon>添加厂商
              </el-button>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 表单对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="480px"
      destroy-on-close
      align-center
      class="manufacturer-dialog"
    >
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        label-width="90px"
        class="manufacturer-form"
      >
        <el-form-item label="全称" prop="name">
          <el-input 
            v-model="form.name" 
            placeholder="请输入全称"
            clearable
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="简称" prop="abbreviation">
          <el-input 
            v-model="form.abbreviation" 
            placeholder="请输入简称（可选）"
            clearable
            maxlength="20"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存修改' : '立即创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { Plus, Edit, Delete, OfficeBuilding, OfficeBuilding as Factory } from '@element-plus/icons-vue';

const holderList = ref([]);
const manufacturerList = ref([]);
const loading1 = ref(false);
const loading2 = ref(false);

const dialogVisible = ref(false);
const dialogType = ref<'holder' | 'manufacturer'>('holder');
const isEdit = ref(false);
const submitting = ref(false);
const formRef = ref<FormInstance>();

const form = reactive({
  id: null as number | null,
  name: '',
  abbreviation: ''
});

const rules: FormRules = {
  name: [{ required: true, message: '请输入全称', trigger: 'blur' }]
};

const dialogTitle = computed(() => {
  const typeText = dialogType.value === 'holder' ? '上市许可持有人' : '生产厂商';
  const actionText = isEdit.value ? '编辑' : '新增';
  return `${actionText}${typeText}`;
});

// 获取上市许可持有人列表
const fetchHolderList = async () => {
  loading1.value = true;
  try {
    const response = await api.get('/syyb/manufacturerholder/');
    holderList.value = response.data.results || [];
  } catch (error) {
    console.error('获取上市许可持有人失败:', error);
  } finally {
    loading1.value = false;
  }
};

// 获取生产厂商列表
const fetchManufacturerList = async () => {
  loading2.value = true;
  try {
    const response = await api.get('/syyb/manufacturer/');
    manufacturerList.value = response.data.results || [];
  } catch (error) {
    console.error('获取生产厂商失败:', error);
  } finally {
    loading2.value = false;
  }
};

// 新增上市许可持有人
const handleAddHolder = () => {
  dialogType.value = 'holder';
  isEdit.value = false;
  form.id = null;
  form.name = '';
  form.abbreviation = '';
  dialogVisible.value = true;
};

// 编辑上市许可持有人
const handleEditHolder = (row: any) => {
  dialogType.value = 'holder';
  isEdit.value = true;
  form.id = row.id;
  form.name = row.name;
  form.abbreviation = row.abbreviation || '';
  dialogVisible.value = true;
};

// 删除上市许可持有人
const handleDeleteHolder = (row: any) => {
  ElMessageBox.confirm(`确定要删除 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/manufacturerholder/${row.id}/`);
      ElMessage.success('删除成功');
      fetchHolderList();
    } catch (error) {
      console.error('删除失败:', error);
    }
  });
};

// 新增生产厂商
const handleAddManufacturer = () => {
  dialogType.value = 'manufacturer';
  isEdit.value = false;
  form.id = null;
  form.name = '';
  form.abbreviation = '';
  dialogVisible.value = true;
};

// 编辑生产厂商
const handleEditManufacturer = (row: any) => {
  dialogType.value = 'manufacturer';
  isEdit.value = true;
  form.id = row.id;
  form.name = row.name;
  form.abbreviation = row.abbreviation || '';
  dialogVisible.value = true;
};

// 删除生产厂商
const handleDeleteManufacturer = (row: any) => {
  ElMessageBox.confirm(`确定要删除 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/manufacturer/${row.id}/`);
      ElMessage.success('删除成功');
      fetchManufacturerList();
    } catch (error) {
      console.error('删除失败:', error);
    }
  });
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        const endpoint = dialogType.value === 'holder' ? 'manufacturerholder' : 'manufacturer';
        const payload = {
          name: form.name,
          abbreviation: form.abbreviation || null
        };
        
        if (isEdit.value && form.id) {
          await api.put(`/syyb/${endpoint}/${form.id}/`, payload);
        } else {
          await api.post(`/syyb/${endpoint}/`, payload);
        }
        
        ElMessage.success(isEdit.value ? '更新成功' : '添加成功');
        dialogVisible.value = false;
        
        if (dialogType.value === 'holder') {
          fetchHolderList();
        } else {
          fetchManufacturerList();
        }
      } catch (error) {
        console.error('提交失败:', error);
      } finally {
        submitting.value = false;
      }
    }
  });
};

onMounted(() => {
  fetchHolderList();
  fetchManufacturerList();
});
</script>

<style scoped>
.manufacturer-page {
  padding: 0;
}

.manufacturer-card {
  border-radius: 12px;
  border: none;
  transition: all 0.3s ease;
}

.manufacturer-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.icon-wrapper.blue {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
}

.icon-wrapper.green {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
}

.title-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.subtitle {
  font-size: 12px;
  color: #909399;
}

.count-tag {
  font-weight: normal;
}

.add-btn {
  border-radius: 8px;
  padding: 8px 16px;
}

/* 表格容器 */
.table-container {
  min-height: 400px;
}

/* 自定义表格样式 */
.custom-table {
  border-radius: 8px;
  overflow: hidden;
}

.custom-table :deep(.el-table__header-wrapper th) {
  font-weight: 600;
  color: #606266;
  height: 44px;
  background-color: #f5f7fa !important;
}

.custom-table :deep(.el-table__row) {
  transition: all 0.2s;
}

.custom-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

/* ID 徽章 */
.id-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  border-radius: 6px;
  background-color: #f0f2f5;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
}

/* 操作组 */
.action-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-group .el-button {
  padding: 4px 8px;
}

/* 空文本 */
.empty-text {
  color: #c0c4cc;
}

/* 对话框样式 */
.manufacturer-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.manufacturer-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.manufacturer-dialog :deep(.el-dialog__title) {
  font-weight: 600;
  font-size: 18px;
  color: #303133;
}

.manufacturer-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.manufacturer-form :deep(.el-input__wrapper) {
  border-radius: 8px;
}

/* 空状态 */
:deep(.el-empty) {
  padding: 60px 0;
}

:deep(.el-empty__description) {
  color: #909399;
  margin-bottom: 16px;
}

/* 标签样式 */
:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
}

/* 分割线 */
:deep(.el-divider--vertical) {
  margin: 0 8px;
}
</style>
