<template>
  <div class="manufacturer-page">
    <el-row :gutter="20">
      <!-- 上市许可持有人 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>上市许可持有人</span>
              <el-button type="primary" size="small" @click="handleAddHolder">
                <el-icon><Plus /></el-icon>新增
              </el-button>
            </div>
          </template>
          
          <el-table :data="holderList" v-loading="loading1" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="全称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="abbreviation" label="简称" width="120" />
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditHolder(row)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="handleDeleteHolder(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <!-- 生产厂商 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>生产厂商</span>
              <el-button type="primary" size="small" @click="handleAddManufacturer">
                <el-icon><Plus /></el-icon>新增
              </el-button>
            </div>
          </template>
          
          <el-table :data="manufacturerList" v-loading="loading2" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="全称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="abbreviation" label="简称" width="120" />
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditManufacturer(row)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="handleDeleteManufacturer(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="450px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="全称" prop="name">
          <el-input v-model="form.name" placeholder="请输入全称" />
        </el-form-item>
        <el-form-item label="简称" prop="abbreviation">
          <el-input v-model="form.abbreviation" placeholder="请输入简称（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';

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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
