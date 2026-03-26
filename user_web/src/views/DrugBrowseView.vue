<template>
  <div class="drug-browse-page">
    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索药品名/商品名/厂商"
            clearable
            style="width: 280px"
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
    </el-card>
    
    <!-- 药品卡片网格 -->
    <div v-loading="loading" class="drug-grid">
      <div
        v-for="drug in drugs"
        :key="drug.id"
        class="drug-card"
        @click="handleView(drug)"
      >
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
          <el-button type="success" text size="small" @click="handleAddToCabinet(drug)">
            <el-icon><Box /></el-icon>加入药箱
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <el-empty v-if="!loading && drugs.length === 0" description="暂无药品数据" />
    
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
    
    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="药品详情" width="700px" destroy-on-close>
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
            </div>
          </div>
        </div>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="规格">{{ currentDrug.specification || '-' }}</el-descriptions-item>
          <el-descriptions-item label="剂型">{{ currentDrug.dosage_form || '-' }}</el-descriptions-item>
          <el-descriptions-item label="生产厂商">{{ currentDrug.manufacturer_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="批准文号">{{ currentDrug.approval_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分类" :span="2">{{ currentDrug.type2_drug_name || '-' }}</el-descriptions-item>
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
        
        <!-- 用药提示 -->
        <div class="detail-section medical-warning">
          <el-alert
            title="用药提示"
            description="此用药说明仅供参考，用药前请咨询专业医生。"
            type="warning"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="success" @click="handleAddToCabinet(currentDrug); viewDialogVisible = false;">
          <el-icon><Box /></el-icon>加入药箱
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 添加到药箱对话框 -->
    <el-dialog v-model="addToCabinetDialogVisible" title="添加药品到药箱" width="550px" destroy-on-close>
      <div v-if="currentDrugForCabinet" class="drug-preview">
        <div class="drug-preview-info">
          <p class="name">{{ currentDrugForCabinet.trade_name || currentDrugForCabinet.drug_name }}</p>
          <p class="spec">{{ currentDrugForCabinet.specification || '-' }}</p>
        </div>
      </div>
      
      <el-form :model="addToCabinetForm" label-width="100px">
        <el-form-item label="选择药箱" required>
          <el-select v-model="addToCabinetForm.cabinet" placeholder="请选择药箱" style="width: 100%">
            <el-option
              v-for="item in cabinetOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量">
              <el-input-number v-model="addToCabinetForm.quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="addToCabinetForm.unit" placeholder="如：片、粒、瓶" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产日期">
              <el-date-picker v-model="addToCabinetForm.production_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至">
              <el-date-picker v-model="addToCabinetForm.valid_until" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="批号">
          <el-input v-model="addToCabinetForm.batch_number" placeholder="请输入批号" />
        </el-form-item>
        <el-form-item label="提醒天数">
          <el-input-number v-model="addToCabinetForm.remind_before_days" :min="1" :max="365" style="width: 100%" />
          <span class="form-tip">过期前 {{ addToCabinetForm.remind_before_days }} 天提醒您</span>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="addToCabinetForm.notes" type="textarea" rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addToCabinetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAddToCabinetSubmit">添加到药箱</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'
import { 
  Search, FirstAidKit, Box, Document, View, InfoFilled 
} from '@element-plus/icons-vue'

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: []
})

// 药品数据
const drugs = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(14)
const total = ref(0)

// 分类选项
const categoryOptions = ref([])

// 查看详情对话框
const viewDialogVisible = ref(false)
const currentDrug = ref<any>(null)

// 添加到药箱对话框
const addToCabinetDialogVisible = ref(false)
const currentDrugForCabinet = ref<any>(null)
const addToCabinetForm = reactive({
  cabinet: null as number | null,
  quantity: 1,
  unit: '',
  production_date: '',
  valid_until: '',
  batch_number: '',
  remind_before_days: 7,
  notes: ''
})
const cabinetOptions = ref<any[]>([])
const submitting = ref(false)

// 获取药品列表
const fetchDrugs = async () => {
  loading.value = true
  try {
    const response = await api.get('/syyb/drug/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    let drugsList = response.data.results || []
    
    // 排序：有图片的排在前面
    drugsList.sort((a: any, b: any) => {
      const aHasImage = a.drug_image ? 1 : 0
      const bHasImage = b.drug_image ? 1 : 0
      // 先按是否有图片排序（有图片的在前）
      if (aHasImage !== bHasImage) {
        return bHasImage - aHasImage
      }
      // 都有图片或都没有图片时，按热门状态排序
      const aIsHot = a.is_hot ? 1 : 0
      const bIsHot = b.is_hot ? 1 : 0
      if (aIsHot !== bIsHot) {
        return bIsHot - aIsHot
      }
      // 最后按ID倒序
      return b.id - a.id
    })
    
    drugs.value = drugsList
    total.value = response.data.count || 0
  } catch (error) {
    console.error('获取药品列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取分类选项
const fetchCategories = async () => {
  try {
    const response = await api.get('/syyb/all_type1_with_type2/')
    categoryOptions.value = response.data.results || []
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  if (searchForm.keyword) {
    searchDrugs()
  } else {
    fetchDrugs()
  }
}

// 模糊搜索药品
const searchDrugs = async () => {
  loading.value = true
  try {
    const response = await api.post('/syyb/search_anything/', {
      text: searchForm.keyword
    })
    let drugsList = response.data.results || []
    
    // 排序：有图片的排在前面
    drugsList.sort((a: any, b: any) => {
      const aHasImage = a.drug_image ? 1 : 0
      const bHasImage = b.drug_image ? 1 : 0
      if (aHasImage !== bHasImage) {
        return bHasImage - aHasImage
      }
      const aIsHot = a.is_hot ? 1 : 0
      const bIsHot = b.is_hot ? 1 : 0
      if (aIsHot !== bIsHot) {
        return bIsHot - aIsHot
      }
      return b.id - a.id
    })
    
    drugs.value = drugsList
    total.value = response.data.count || 0
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    loading.value = false
  }
}

// 重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.category = []
  currentPage.value = 1
  fetchDrugs()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchDrugs()
}

const handlePageChange = (val: number) => {
  currentPage.value = val
  fetchDrugs()
}

// 查看详情
const handleView = (row: any) => {
  currentDrug.value = row
  viewDialogVisible.value = true
}

// 获取医保类型标签样式
const getInsuranceType = (type: string) => {
  const map: Record<string, string> = {
    '甲类': 'danger',
    '乙类': 'warning',
    '非医保': 'info'
  }
  return map[type] || 'info'
}

// 获取药箱选项
const fetchCabinetOptions = async () => {
  try {
    const response = await api.get('/syyb/cabinets/')
    cabinetOptions.value = (response.data.results || []).map((c: any) => ({
      label: c.name + (c.is_default ? ' (默认)' : ''),
      value: c.id
    }))
    const defaultCabinet = response.data.results?.find((c: any) => c.is_default)
    if (defaultCabinet) {
      addToCabinetForm.cabinet = defaultCabinet.id
    }
  } catch (error) {
    console.error('获取药箱列表失败:', error)
  }
}

// 添加到药箱
const handleAddToCabinet = (row: any) => {
  currentDrugForCabinet.value = row
  fetchCabinetOptions()
  Object.assign(addToCabinetForm, {
    cabinet: null,
    quantity: 1,
    unit: row.specification || '盒',
    production_date: '',
    valid_until: '',
    batch_number: '',
    remind_before_days: 7,
    notes: ''
  })
  addToCabinetDialogVisible.value = true
}

// 提交添加到药箱
const handleAddToCabinetSubmit = async () => {
  if (!currentDrugForCabinet.value || !addToCabinetForm.cabinet) {
    ElMessage.warning('请选择药箱')
    return
  }
  
  submitting.value = true
  try {
    await api.post('/syyb/cabinet_drugs/', {
      cabinet: addToCabinetForm.cabinet,
      drug: currentDrugForCabinet.value.id,
      quantity: addToCabinetForm.quantity,
      unit: addToCabinetForm.unit,
      production_date: addToCabinetForm.production_date,
      valid_until: addToCabinetForm.valid_until,
      batch_number: addToCabinetForm.batch_number,
      remind_before_days: addToCabinetForm.remind_before_days,
      notes: addToCabinetForm.notes
    })
    ElMessage.success('添加成功')
    addToCabinetDialogVisible.value = false
  } catch (error) {
    console.error('添加失败:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchDrugs()
  fetchCategories()
})
</script>

<style scoped>
.drug-browse-page {
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
  border-color: #409eff;
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

/* 添加到药箱对话框 */
.drug-preview {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.drug-preview-info .name {
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.drug-preview-info .spec {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .drug-grid {
    grid-template-columns: 1fr;
  }
}
</style>
