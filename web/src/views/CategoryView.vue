<template>
  <div class="category-page">
    <el-row :gutter="20">
      <!-- 一级分类 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>一级分类</span>
              <el-button type="primary" size="small" @click="handleAddType1">
                <el-icon><Plus /></el-icon>新增
              </el-button>
            </div>
          </template>
          
          <el-table :data="type1List" v-loading="loading1" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="分类名称" />
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditType1(row)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="handleDeleteType1(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <!-- 二级分类 -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>二级分类</span>
              <el-button type="primary" size="small" :disabled="!selectedType1" @click="handleAddType2">
                <el-icon><Plus /></el-icon>新增
              </el-button>
            </div>
          </template>
          
          <div v-if="!selectedType1" class="empty-tip">
            <el-icon :size="48" color="#dcdfe6"><Collection /></el-icon>
            <p>请先选择左侧一级分类</p>
          </div>
          
          <el-table v-else :data="type2List" v-loading="loading2" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="分类名称" />
            <el-table-column prop="drugs_count" label="药品数量" width="100" align="center" />
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditType2(row)">
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="handleDeleteType2(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分类表单对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="400px">
      <el-form :model="categoryForm" :rules="categoryRules" ref="formRef" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
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

const type1List = ref([]);
const type2List = ref([]);
const loading1 = ref(false);
const loading2 = ref(false);
const selectedType1 = ref<number | null>(null);

const dialogVisible = ref(false);
const dialogType = ref<'type1' | 'type2'>('type1');
const isEdit = ref(false);
const submitting = ref(false);
const formRef = ref<FormInstance>();

const categoryForm = reactive({
  id: null as number | null,
  name: ''
});

const categoryRules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
};

const dialogTitle = computed(() => {
  const typeText = dialogType.value === 'type1' ? '一级' : '二级';
  const actionText = isEdit.value ? '编辑' : '新增';
  return `${actionText}${typeText}分类`;
});

// 获取一级分类
const fetchType1List = async () => {
  loading1.value = true;
  try {
    const response = await api.get('/syyb/type1drug/');
    type1List.value = response.data.results || [];
  } catch (error) {
    console.error('获取一级分类失败:', error);
  } finally {
    loading1.value = false;
  }
};

// 获取二级分类
const fetchType2List = async (type1Id: number) => {
  loading2.value = true;
  try {
    const response = await api.get(`/syyb/type1_type2/${type1Id}/`);
    type2List.value = response.data || [];
  } catch (error) {
    console.error('获取二级分类失败:', error);
  } finally {
    loading2.value = false;
  }
};

// 选择一级分类
const selectType1 = (row: any) => {
  selectedType1.value = row.id;
  fetchType2List(row.id);
};

// 新增一级分类
const handleAddType1 = () => {
  dialogType.value = 'type1';
  isEdit.value = false;
  categoryForm.id = null;
  categoryForm.name = '';
  dialogVisible.value = true;
};

// 编辑一级分类
const handleEditType1 = (row: any) => {
  dialogType.value = 'type1';
  isEdit.value = true;
  categoryForm.id = row.id;
  categoryForm.name = row.name;
  dialogVisible.value = true;
};

// 删除一级分类
const handleDeleteType1 = (row: any) => {
  ElMessageBox.confirm(`确定要删除分类 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/type1drug/${row.id}/`);
      ElMessage.success('删除成功');
      fetchType1List();
    } catch (error) {
      console.error('删除失败:', error);
    }
  });
};

// 新增二级分类
const handleAddType2 = () => {
  if (!selectedType1.value) return;
  dialogType.value = 'type2';
  isEdit.value = false;
  categoryForm.id = null;
  categoryForm.name = '';
  dialogVisible.value = true;
};

// 编辑二级分类
const handleEditType2 = (row: any) => {
  dialogType.value = 'type2';
  isEdit.value = true;
  categoryForm.id = row.id;
  categoryForm.name = row.name;
  dialogVisible.value = true;
};

// 删除二级分类
const handleDeleteType2 = (row: any) => {
  ElMessageBox.confirm(`确定要删除分类 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/type2drug/${row.id}/`);
      ElMessage.success('删除成功');
      if (selectedType1.value) {
        fetchType2List(selectedType1.value);
      }
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
        const endpoint = dialogType.value === 'type1' ? 'type1drug' : 'type2drug';
        const payload = dialogType.value === 'type1'
          ? { name: categoryForm.name }
          : { name: categoryForm.name, type1_drug: selectedType1.value };
        
        if (isEdit.value && categoryForm.id) {
          await api.put(`/syyb/${endpoint}/${categoryForm.id}/`, payload);
        } else {
          await api.post(`/syyb/${endpoint}/`, payload);
        }
        
        ElMessage.success(isEdit.value ? '更新成功' : '添加成功');
        dialogVisible.value = false;
        
        if (dialogType.value === 'type1') {
          fetchType1List();
        } else if (selectedType1.value) {
          fetchType2List(selectedType1.value);
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
  fetchType1List();
});
</script>

<style scoped>
.category-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-tip p {
  margin-top: 16px;
}
</style>
