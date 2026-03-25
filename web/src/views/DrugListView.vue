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
          <el-icon><Delete /></el-icon>批量删除({{ selectedDrugs.length }})
        </el-button>
      </div>
    </el-card>
    
    <!-- 药品卡片网格 -->
    <div v-loading="loading" class="drug-grid">
      <div
        v-for="drug in drugs"
        :key="drug.id"
        :class="['drug-card', { selected: isSelected(drug) }]"
        @click="toggleSelection(drug)"
      >
        <!-- 选中标记 -->
        <div v-if="isSelected(drug)" class="selected-badge">
          <el-icon><Check /></el-icon>
        </div>
        
        <!-- 热门标记 -->
        <div v-if="drug.is_hot" class="hot-badge">热</div>
        
        <!-- 药品图片 -->
        <div class="drug-image-wrapper">
          <el-image
            :src="drug.drug_image || '/default-drug.png'"
            fit="cover"
            class="drug-image"
          >
            <template #error>
              <div class="image-placeholder">
                <el-icon :size="40"><FirstAidKit /></el-icon>
              </div>
            </template>
          </el-image>
        </div>
        
        <!-- 药品信息 -->
        <div class="drug-info">
          <h4 class="drug-title">{{ drug.trade_name || drug.drug_name }}</h4>
          <p v-if="drug.trade_name" class="drug-subtitle">{{ drug.drug_name }}</p>
          
          <div class="drug-tags">
            <el-tag v-if="drug.medical_insurance" :type="getInsuranceType(drug.medical_insurance)" size="small">
              {{ drug.medical_insurance }}
            </el-tag>
            <el-tag v-if="drug.dosage_form" type="info" size="small" effect="plain">
              {{ drug.dosage_form }}
            </el-tag>
          </div>
          
          <p class="drug-spec">{{ drug.specification || '暂无规格信息' }}</p>
          
          <div v-if="drug.indications" class="drug-indications">
            <el-icon :size="14" color="#67C23A"><FirstAidKit /></el-icon>
            <span>{{ drug.indications }}</span>
          </div>
          <p v-else class="drug-no-indications">
            <el-icon :size="14" color="#909399"><InfoFilled /></el-icon>
            <span>暂无适用症状信息</span>
          </p>
        </div>
        
        <!-- 操作按钮 -->
        <div class="drug-actions" @click.stop>
          <el-button type="primary" text size="small" @click="handleView(drug)">
            <el-icon><View /></el-icon>详情
          </el-button>
          <el-button type="primary" text size="small" @click="handleEdit(drug)">
            <el-icon><Edit /></el-icon>编辑
          </el-button>
          <el-button type="danger" text size="small" @click="handleDelete(drug)">
            <el-icon><Delete /></el-icon>删除
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <el-empty v-if="!loading && drugs.length === 0" description="暂无药品数据">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>添加药品
      </el-button>
    </el-empty>
    
    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[14, 28, 56, 112]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
    
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
        
        <el-form-item label="适用症状" prop="indications">
          <el-input 
            v-model="drugForm.indications" 
            type="textarea" 
            :rows="3"
            placeholder="请输入适用症状，如：感冒、发热、头痛等"
          />
        </el-form-item>
        
        <el-form-item label="药品说明" prop="description">
          <el-input 
            v-model="drugForm.description" 
            type="textarea" 
            :rows="5"
            placeholder="请输入药品详细说明（用法用量、注意事项、不良反应等）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="药品详情"
      width="700px"
      destroy-on-close
    >
      <div v-if="currentDrug" class="drug-detail">
        <div class="detail-header">
          <div class="detail-image">
            <el-image
              :src="currentDrug.drug_image || '/default-drug.png'"
              fit="cover"
              style="width: 120px; height: 120px; border-radius: 8px"
            >
              <template #error>
                <div class="image-placeholder-large">
                  <el-icon :size="48"><FirstAidKit /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
          <div class="detail-title">
            <h2>{{ currentDrug.trade_name || '-' }}</h2>
            <p class="subtitle">{{ currentDrug.drug_name || '-' }}</p>
            <div class="detail-tags">
              <el-tag v-if="currentDrug.is_hot" type="danger" effect="dark">热门</el-tag>
              <el-tag v-if="currentDrug.medical_insurance" :type="getInsuranceType(currentDrug.medical_insurance)">
                {{ currentDrug.medical_insurance }}
              </el-tag>
              <el-tag v-if="currentDrug.market_status" :type="getMarketStatusType(currentDrug.market_status)">
                {{ currentDrug.market_status }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="规格">{{ currentDrug.specification || '-' }}</el-descriptions-item>
          <el-descriptions-item label="剂型">{{ currentDrug.dosage_form || '-' }}</el-descriptions-item>
          <el-descriptions-item label="给药途径">{{ currentDrug.administration_route || '-' }}</el-descriptions-item>
          <el-descriptions-item label="批准文号">{{ currentDrug.approval_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="批准日期">{{ currentDrug.approval_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="ATC编码">{{ currentDrug.atc_code || '-' }}</el-descriptions-item>
          <el-descriptions-item label="一级分类">{{ currentDrug.type1_drug || '-' }}</el-descriptions-item>
          <el-descriptions-item label="二级分类">{{ currentDrug.type2_drug_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="生产厂商">{{ currentDrug.manufacturer_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="上市许可持有人">{{ currentDrug.manufacturer_holder_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="活性成分">{{ currentDrug.active_ingredient || '-' }}</el-descriptions-item>
          <el-descriptions-item label="医保类型">{{ currentDrug.medical_insurance || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentDrug.indications" class="detail-section">
          <h4 class="section-title">
            <el-icon><FirstAidKit /></el-icon>
            适用症状
          </h4>
          <div class="section-content">{{ currentDrug.indications }}</div>
        </div>
        
        <div v-if="currentDrug.description" class="detail-section">
          <h4 class="section-title">
            <el-icon><Document /></el-icon>
            药品说明
          </h4>
          <div class="section-content description-text">{{ currentDrug.description }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEdit(currentDrug); viewDialogVisible = false;">
          <el-icon><Edit /></el-icon>编辑
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入药品"
      width="800px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-steps :active="importStep" finish-status="success" simple class="import-steps">
        <el-step title="上传文件" />
        <el-step title="预览数据" />
        <el-step title="导入完成" />
      </el-steps>
      
      <div v-if="importStep === 1" class="import-step-content">
        <div class="template-download">
          <p>请先下载导入模板，按照模板格式填写数据</p>
          <el-button type="primary" plain @click="downloadTemplate">
            <el-icon><Download /></el-icon>下载导入模板
          </el-button>
        </div>
        
        <el-divider>或</el-divider>
        
        <el-upload
          class="upload-area"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="true"
          accept=".xls,.xlsx,.xlsm"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
        </el-upload>
      </div>
      
      <div v-if="importStep === 2" class="import-step-content">
        <el-alert title="数据预览" description="请检查以下数据是否正确，确认无误后点击导入" type="info" show-icon :closable="false" />
        <el-table :data="previewData" height="300" stripe border>
          <el-table-column type="index" label="行号" width="60" align="center" />
          <el-table-column prop="drug_name" label="药品名称" min-width="120" />
          <el-table-column prop="trade_name" label="商品名" min-width="120" />
          <el-table-column prop="specification" label="规格" width="100" />
          <el-table-column prop="manufacturer_name" label="生产厂商" min-width="120" />
        </el-table>
      </div>
      
      <div v-if="importStep === 3" class="import-step-content">
        <el-result
          :icon="importResults.success ? 'success' : 'error'"
          :title="importResults.success ? '导入成功' : '导入失败'"
          :sub-title="importResults.message"
        />
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button v-if="importStep > 1 && importStep < 3" @click="importStep--">上一步</el-button>
          <el-button v-if="importStep === 1" @click="importDialogVisible = false">取消</el-button>
          <el-button v-if="importStep === 1" type="primary" :disabled="!uploadFile" @click="previewImport">下一步</el-button>
          <el-button v-if="importStep === 2" type="primary" :loading="importing" @click="confirmImport">确认导入</el-button>
          <el-button v-if="importStep === 3" type="primary" @click="importDialogVisible = false">完成</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { 
  Search, Plus, Upload, Delete, Edit, View, FirstAidKit, 
  Box, Download, Document, Check, InfoFilled 
} from '@element-plus/icons-vue';

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: []
});

// 药品数据
const drugs = ref([]);
const loading = ref(false);
const selectedDrugs = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(14);
const total = ref(0);

// 分类选项
const categoryOptions = ref([]);

// 厂商选项
const manufacturerOptions = ref<any[]>([]);

// 新增/编辑对话框
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
  approval_number: '',
  description: '',
  indications: ''
});

const drugRules: FormRules = {
  drug_name: [{ required: true, message: '请输入通用名', trigger: 'blur' }],
  trade_name: [{ required: true, message: '请输入商品名', trigger: 'blur' }],
  manufacturer: [{ required: true, message: '请选择生产厂商', trigger: 'change' }]
};

// 查看详情对话框
const viewDialogVisible = ref(false);
const currentDrug = ref<any>(null);

// 批量导入
const importDialogVisible = ref(false);
const importStep = ref(1);
const uploadFile = ref<File | null>(null);
const previewData = ref<any[]>([]);
const importResults = ref({ success: false, message: '' });
const importing = ref(false);

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
    categoryOptions.value = response.data.results || [];
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

// 获取医保类型标签样式
const getInsuranceType = (type: string) => {
  const map: Record<string, string> = {
    '甲类': 'danger',
    '乙类': 'warning',
    '非医保': 'info'
  };
  return map[type] || 'info';
};

// 获取市场状态标签样式
const getMarketStatusType = (status: string) => {
  const map: Record<string, string> = {
    '在售': 'success',
    '停产': 'info',
    '退市': 'danger'
  };
  return map[status] || 'info';
};

// 是否选中
const isSelected = (drug: any) => {
  return selectedDrugs.value.some(d => d.id === drug.id);
};

// 切换选中状态
const toggleSelection = (drug: any) => {
  const index = selectedDrugs.value.findIndex(d => d.id === drug.id);
  if (index > -1) {
    selectedDrugs.value.splice(index, 1);
  } else {
    selectedDrugs.value.push(drug);
  }
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

// 查看详情
const handleView = (row: any) => {
  currentDrug.value = row;
  viewDialogVisible.value = true;
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
      selectedDrugs.value = [];
      fetchDrugs();
    } catch (error) {
      console.error('批量删除失败:', error);
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
  drugForm.description = '';
  drugForm.indications = '';
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

// 批量导入
const handleImport = () => {
  importStep.value = 1;
  uploadFile.value = null;
  previewData.value = [];
  importDialogVisible.value = true;
};

// 下载导入模板
const downloadTemplate = async () => {
  try {
    const response = await api.get('/syyb/download_import_template/', {
      responseType: 'blob'
    });
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = '药品导入模板.xlsx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    ElMessage.success('模板下载成功');
  } catch (error) {
    console.error('下载模板失败:', error);
    ElMessage.error('下载模板失败');
  }
};

// 文件选择变化
const handleFileChange = (file: File) => {
  const isExcel = file.name.endsWith('.xls') || file.name.endsWith('.xlsx') || file.name.endsWith('.xlsm');
  if (!isExcel) {
    ElMessage.error('请上传 Excel 文件 (.xls, .xlsx, .xlsm)');
    return false;
  }
  uploadFile.value = file;
  return false;
};

// 预览导入数据
const previewImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请先选择文件');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', uploadFile.value);
  
  try {
    const response = await api.post('/syyb/preview_import_excel/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    if (response.data.success) {
      previewData.value = response.data.preview_data || [];
      importStep.value = 2;
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '预览失败');
  }
};

// 确认导入
const confirmImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('文件已丢失，请重新选择');
    return;
  }
  
  importing.value = true;
  const formData = new FormData();
  formData.append('file', uploadFile.value);
  
  try {
    const response = await api.post('/syyb/add_drugs_from_excel/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    if (response.data.success) {
      importResults.value = {
        success: true,
        message: response.data.message
      };
      importStep.value = 3;
      fetchDrugs();
    }
  } catch (error: any) {
    importResults.value = {
      success: false,
      message: error.response?.data?.error || '导入失败'
    };
  } finally {
    importing.value = false;
  }
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
  border-radius: 12px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.operation-bar {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* 药品卡片网格 */
.drug-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.drug-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 2px solid transparent;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.drug-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.drug-card.selected {
  border-color: #409eff;
}

.selected-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.hot-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f56c6c;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  z-index: 10;
}

.drug-image-wrapper {
  height: 160px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.drug-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.drug-info {
  padding: 16px;
}

.drug-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0 0 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.drug-spec {
  font-size: 13px;
  color: #606266;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-indications {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #67c23a;
  margin: 8px 0 0 0;
  line-height: 1.5;
  padding: 8px 10px;
  background: #f0f9eb;
  border-radius: 6px;
  min-height: 36px;
}

.drug-indications span {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-no-indications {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #909399;
  margin: 8px 0 0 0;
  padding: 8px 10px;
  background: #f5f7fa;
  border-radius: 6px;
  min-height: 36px;
}

.drug-actions {
  display: flex;
  justify-content: space-around;
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  background: #fafafa;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0;
}

/* 详情对话框 */
.drug-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.detail-image {
  flex-shrink: 0;
}

.image-placeholder-large {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  color: #c0c4cc;
}

.detail-title {
  flex: 1;
}

.detail-title h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.detail-title .subtitle {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.detail-tags {
  display: flex;
  gap: 8px;
}

.detail-descriptions {
  margin-bottom: 20px;
}

.detail-section {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #303133;
}

.section-content {
  color: #606266;
  line-height: 1.6;
}

.description-text {
  white-space: pre-wrap;
}

/* 导入对话框 */
.import-steps {
  margin-bottom: 20px;
}

.import-step-content {
  padding: 20px 0;
}

.template-download {
  text-align: center;
  padding: 40px 20px;
}

.template-download p {
  margin-bottom: 16px;
  color: #606266;
}

.upload-area {
  width: 100%;
}

/* 响应式 */
@media (max-width: 768px) {
  .drug-grid {
    grid-template-columns: 1fr;
  }
}
</style>
