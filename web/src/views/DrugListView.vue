<template>
  <div class="drug-list-page">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="药品名/商品名/厂商"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="分类">
          <el-cascader
            v-model="searchForm.category"
            :options="categoryOptions"
            :props="{ checkStrictly: true, label: 'label', value: 'value' }"
            placeholder="选择分类"
            clearable
            style="width: 200px"
          />
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
          <el-icon><Plus /></el-icon>新增药品
        </el-button>
        <el-button type="success" @click="handleImport">
          <el-icon><Upload /></el-icon>批量导入
        </el-button>
        <el-button type="danger" :disabled="!selectedDrugs.length" @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>批量删除
        </el-button>
      </div>
    </el-card>
    
    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        :data="drugs"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
        border
        highlight-current-row
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="id" label="ID" width="80" align="center" />
        
        <el-table-column label="药品图片" width="100" align="center">
          <template #default="{ row }">
            <el-image
              :src="row.drug_image || '/default-drug.png'"
              :preview-src-list="[row.drug_image]"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 4px"
            >
              <template #error>
                <div class="image-placeholder">
                  <el-icon :size="24"><First-Aid-Kit /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        
        <el-table-column prop="trade_name" label="商品名" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="drug-name">
              <span class="name">{{ row.trade_name || '-' }}</span>
              <el-tag v-if="row.is_hot" type="danger" size="small" effect="plain">热门</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="drug_name" label="通用名" min-width="150" show-overflow-tooltip />
        
        <el-table-column prop="specification" label="规格" width="120" show-overflow-tooltip />
        
        <el-table-column prop="dosage_form" label="剂型" width="100" />
        
        <el-table-column prop="manufacturer_name" label="生产厂商" min-width="180" show-overflow-tooltip />
        
        <el-table-column prop="approval_number" label="批准文号" width="140" />
        
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              删除
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
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑药品' : '新增药品'"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="drugForm"
        :rules="drugRules"
        label-width="100px"
        class="drug-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="通用名" prop="drug_name">
              <el-input v-model="drugForm.drug_name" placeholder="请输入通用名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名" prop="trade_name">
              <el-input v-model="drugForm.trade_name" placeholder="请输入商品名" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格" prop="specification">
              <el-input v-model="drugForm.specification" placeholder="请输入规格" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="剂型" prop="dosage_form">
              <el-input v-model="drugForm.dosage_form" placeholder="请输入剂型" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="生产厂商" prop="manufacturer">
          <el-select
            v-model="drugForm.manufacturer"
            placeholder="选择生产厂商"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="item in manufacturerOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="批准文号" prop="approval_number">
          <el-input v-model="drugForm.approval_number" placeholder="请输入批准文号" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: []
});

// 表格数据
const drugs = ref([]);
const loading = ref(false);
const selectedDrugs = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 分类选项
const categoryOptions = ref([]);

// 厂商选项
const manufacturerOptions = ref([]);

// 对话框
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const formRef = ref<FormInstance>();

const drugForm = reactive({
  id: null as number | null,
  drug_name: '',
  trade_name: '',
  specification: '',
  dosage_form: '',
  manufacturer: null as number | null,
  approval_number: ''
});

const drugRules: FormRules = {
  drug_name: [{ required: true, message: '请输入通用名', trigger: 'blur' }],
  trade_name: [{ required: true, message: '请输入商品名', trigger: 'blur' }],
  manufacturer: [{ required: true, message: '请选择生产厂商', trigger: 'change' }]
};

// 获取药品列表
const fetchDrugs = async () => {
  loading.value = true;
  try {
    const response = await api.get('/syyb/drug/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    });
    drugs.value = response.data.results || [];
    total.value = response.data.count || 0;
  } catch (error) {
    console.error('获取药品列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 获取分类选项
const fetchCategories = async () => {
  try {
    const response = await api.get('/syyb/all_type1_with_type2/');
    categoryOptions.value = response.data || [];
  } catch (error) {
    console.error('获取分类失败:', error);
  }
};

// 获取厂商列表
const fetchManufacturers = async () => {
  try {
    const response = await api.get('/syyb/manufacturer/');
    manufacturerOptions.value = response.data.results || [];
  } catch (error) {
    console.error('获取厂商列表失败:', error);
  }
};

// 搜索
const handleSearch = () => {
  currentPage.value = 1;
  if (searchForm.keyword) {
    searchDrugs();
  } else {
    fetchDrugs();
  }
};

// 模糊搜索药品
const searchDrugs = async () => {
  loading.value = true;
  try {
    const response = await api.post('/syyb/search_anything/', {
      text: searchForm.keyword
    });
    drugs.value = response.data.results || [];
    total.value = response.data.count || 0;
  } catch (error) {
    console.error('搜索失败:', error);
  } finally {
    loading.value = false;
  }
};

// 重置
const handleReset = () => {
  searchForm.keyword = '';
  searchForm.category = [];
  currentPage.value = 1;
  fetchDrugs();
};

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedDrugs.value = selection;
};

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  fetchDrugs();
};

const handlePageChange = (val: number) => {
  currentPage.value = val;
  fetchDrugs();
};

// 新增
const handleAdd = () => {
  isEdit.value = false;
  resetForm();
  dialogVisible.value = true;
};

// 编辑
const handleEdit = (row: any) => {
  isEdit.value = true;
  Object.assign(drugForm, row);
  dialogVisible.value = true;
};

// 查看
const handleView = (row: any) => {
  ElMessage.info(`查看药品: ${row.trade_name || row.drug_name}`);
};

// 删除
const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除药品 "${row.trade_name || row.drug_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/drug/${row.id}/`);
      ElMessage.success('删除成功');
      fetchDrugs();
    } catch (error) {
      console.error('删除失败:', error);
    }
  });
};

// 批量删除
const handleBatchDelete = () => {
  const ids = selectedDrugs.value.map((item: any) => item.id);
  ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 个药品吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete('/syyb/batch_delete_drugs/', {
        data: { drug_ids: ids }
      });
      ElMessage.success('批量删除成功');
      fetchDrugs();
    } catch (error) {
      console.error('批量删除失败:', error);
    }
  });
};

// 导入
const handleImport = () => {
  ElMessage.info('批量导入功能开发中');
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        if (isEdit.value && drugForm.id) {
          await api.put(`/syyb/drug/${drugForm.id}/`, drugForm);
          ElMessage.success('更新成功');
        } else {
          await api.post('/syyb/drug/', drugForm);
          ElMessage.success('添加成功');
        }
        dialogVisible.value = false;
        fetchDrugs();
      } catch (error) {
        console.error('提交失败:', error);
      } finally {
        submitting.value = false;
      }
    }
  });
};

// 重置表单
const resetForm = () => {
  drugForm.id = null;
  drugForm.drug_name = '';
  drugForm.trade_name = '';
  drugForm.specification = '';
  drugForm.dosage_form = '';
  drugForm.manufacturer = null;
  drugForm.approval_number = '';
};

onMounted(() => {
  fetchDrugs();
  fetchCategories();
  fetchManufacturers();
});
</script>

<style scoped>
.drug-list-page {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 15px;
}

.operation-bar {
  display: flex;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.table-card {
  min-height: calc(100vh - 280px);
}

.drug-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.drug-name .name {
  font-weight: 500;
}

.image-placeholder {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border-radius: 4px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.drug-form :deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
