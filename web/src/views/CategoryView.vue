<template>
  <div class="category-page">
    <el-row :gutter="24">
      <!-- 一级分类 -->
      <el-col :span="10">
        <el-card shadow="hover" class="category-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon :size="20" color="#409EFF"><Folder /></el-icon>
                <span>一级分类</span>
                <el-tag type="info" size="small" class="count-tag">{{ type1List.length }}</el-tag>
              </div>
              <el-button type="primary" @click="handleAddType1" class="add-btn">
                <el-icon><Plus /></el-icon>新增分类
              </el-button>
            </div>
          </template>
          
          <div v-loading="loading1" class="category-list">
            <div
              v-for="item in type1List"
              :key="item.id"
              :class="['category-item', { active: selectedType1 === item.id }]"
              @click="selectType1(item)"
            >
              <div class="item-content">
                <div class="item-icon">
                  <el-icon :size="18"><FolderOpened v-if="selectedType1 === item.id" /><Folder v-else /></el-icon>
                </div>
                <div class="item-info">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-id">ID: {{ item.id }}</span>
                </div>
              </div>
              <div class="item-actions">
                <el-button 
                  link 
                  type="primary" 
                  :icon="Edit" 
                  @click.stop="handleEditType1(item)"
                  class="action-btn"
                />
                <el-button 
                  link 
                  type="danger" 
                  :icon="Delete" 
                  @click.stop="handleDeleteType1(item)"
                  class="action-btn"
                />
              </div>
            </div>
            
            <el-empty v-if="!loading1 && type1List.length === 0" description="暂无分类数据" />
          </div>
        </el-card>
      </el-col>
      
      <!-- 二级分类 -->
      <el-col :span="14">
        <el-card shadow="hover" class="category-card">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon :size="20" color="#67C23A"><Collection /></el-icon>
                <span>二级分类</span>
                <template v-if="selectedType1">
                  <el-divider direction="vertical" />
                  <el-tag type="success" size="small">{{ selectedType1Name }}</el-tag>
                </template>
                <el-tag v-if="selectedType1" type="info" size="small" class="count-tag">{{ type2List.length }}</el-tag>
              </div>
              <el-button 
                type="success" 
                :disabled="!selectedType1" 
                @click="handleAddType2"
                class="add-btn"
              >
                <el-icon><Plus /></el-icon>新增子分类
              </el-button>
            </div>
          </template>
          
          <div v-if="!selectedType1" class="empty-state">
            <div class="empty-illustration">
              <el-icon :size="64" color="#dcdfe6"><Collection /></el-icon>
            </div>
            <h3 class="empty-title">选择一级分类</h3>
            <p class="empty-desc">点击左侧分类查看和管理对应的二级分类</p>
          </div>
          
          <div v-else v-loading="loading2" class="subcategory-container">
            <div v-if="type2List.length > 0" class="subcategory-grid">
              <div
                v-for="item in type2List"
                :key="item.id"
                class="subcategory-item"
              >
                <div class="subcategory-content">
                  <div class="subcategory-header">
                    <span class="subcategory-name">{{ item.name }}</span>
                    <el-tag v-if="item.drugs_count > 0" type="warning" size="small">
                      {{ item.drugs_count }} 个药品
                    </el-tag>
                    <el-tag v-else type="info" size="small">无药品</el-tag>
                  </div>
                  <div class="subcategory-meta">
                    <span class="meta-item">ID: {{ item.id }}</span>
                  </div>
                </div>
                <div class="subcategory-actions">
                  <el-button 
                    link 
                    type="primary" 
                    :icon="Edit"
                    @click="handleEditType2(item)"
                  >
                    编辑
                  </el-button>
                  <el-button 
                    link 
                    type="danger" 
                    :icon="Delete"
                    @click="handleDeleteType2(item)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>
            
            <el-empty v-else description="该分类下暂无二级分类">
              <el-button type="primary" @click="handleAddType2">
                <el-icon><Plus /></el-icon>添加二级分类
              </el-button>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分类表单对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="420px"
      destroy-on-close
      align-center
    >
      <el-form 
        :model="categoryForm" 
        :rules="categoryRules" 
        ref="formRef" 
        label-width="90px"
        class="category-form"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input 
            v-model="categoryForm.name" 
            placeholder="请输入分类名称"
            clearable
            maxlength="50"
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
import { Plus, Edit, Delete, Folder, FolderOpened, Collection } from '@element-plus/icons-vue';

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

const selectedType1Name = computed(() => {
  const item = type1List.value.find(t => t.id === selectedType1.value);
  return item?.name || '';
});

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
    type2List.value = response.data.results || [];
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
      if (selectedType1.value === row.id) {
        selectedType1.value = null;
      }
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

.category-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.category-card:hover {
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
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.count-tag {
  font-weight: normal;
}

.add-btn {
  border-radius: 8px;
  padding: 8px 16px;
}

/* 一级分类列表 */
.category-list {
  min-height: 300px;
}

.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  margin-bottom: 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  border: 1px solid transparent;
  background-color: #f5f7fa;
}

.category-item:hover {
  background-color: #e6f2ff;
  border-color: #b3d8ff;
  transform: translateX(4px);
}

.category-item.active {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  color: white;
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.category-item.active .item-id {
  color: rgba(255, 255, 255, 0.8);
}

.item-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.2);
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-name {
  font-size: 15px;
  font-weight: 500;
}

.item-id {
  font-size: 12px;
  color: #909399;
}

.item-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.category-item:hover .item-actions,
.category-item.active .item-actions {
  opacity: 1;
}

.action-btn {
  padding: 6px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-illustration {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  margin-bottom: 24px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #909399;
}

/* 二级分类网格 */
.subcategory-container {
  min-height: 300px;
}

.subcategory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.subcategory-item {
  display: flex;
  flex-direction: column;
  padding: 16px;
  border-radius: 12px;
  background-color: #f5f7fa;
  border: 1px solid transparent;
  transition: all 0.25s ease;
}

.subcategory-item:hover {
  background-color: #ffffff;
  border-color: #d9ecff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.subcategory-content {
  flex: 1;
}

.subcategory-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.subcategory-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.subcategory-meta {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.meta-item {
  font-size: 12px;
  color: #909399;
}

.subcategory-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #dcdfe6;
}

/* 表单样式 */
.category-form {
  padding: 20px 10px 0;
}
</style>
