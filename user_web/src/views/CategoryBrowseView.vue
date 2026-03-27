<template>
  <div class="category-browse-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>分类浏览</h2>
      <p>点击分类卡片查看详细信息</p>
    </div>

    <!-- 一级分类卡片网格 -->
    <div v-loading="loading1" class="category-grid">
      <div
        v-for="item in type1List"
        :key="item.id"
        class="category-card"
        @click="handleCategoryClick(item)"
      >
        <div class="category-icon" :style="getIconStyle(item.id)">
          <el-icon :size="40"><component :is="getCategoryIcon(item.name)" /></el-icon>
        </div>
        <div class="category-info">
          <h3 class="category-name">{{ item.name }}</h3>
          <p class="category-desc">{{ getCategoryDesc(item.name) }}</p>
        </div>
        <div class="category-arrow">
          <el-icon :size="20"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading1 && type1List.length === 0" description="暂无分类数据" />

    <!-- 二级分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="selectedType1?.name"
      width="800px"
      top="5vh"
      destroy-on-close
      class="subcategory-dialog"
    >
      <div v-loading="loading2" class="subcategory-content">
        <!-- 二级分类网格 -->
        <div v-if="type2List.length > 0" class="subcategory-grid">
          <div
            v-for="item in type2List"
            :key="item.id"
            class="subcategory-card"
            @click="viewDrugsByCategory(item)"
          >
            <div class="subcategory-icon">
              <el-icon :size="24"><Folder /></el-icon>
            </div>
            <div class="subcategory-info">
              <span class="subcategory-name">{{ item.name }}</span>
              <el-tag v-if="item.drugs_count > 0" type="primary" size="small" effect="light">
                {{ item.drugs_count }} 个药品
              </el-tag>
              <el-tag v-else type="info" size="small" effect="light">暂无药品</el-tag>
            </div>
            <el-icon class="subcategory-arrow" :size="16"><ArrowRight /></el-icon>
          </div>
        </div>

        <el-empty v-else description="该分类下暂无二级分类" />
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 药品列表对话框 - 卡片形式 -->
    <el-dialog
      v-model="drugsDialogVisible"
      :title="`${selectedType2Name} - 药品列表`"
      width="1000px"
      top="3vh"
      destroy-on-close
      class="drugs-dialog"
    >
      <div v-loading="drugsLoading" class="drugs-content">
        <!-- 药品卡片网格 -->
        <div v-if="categoryDrugs.length > 0" class="drug-cards-grid">
          <div
            v-for="drug in categoryDrugs"
            :key="drug.id"
            class="drug-card-item"
            @click="handleViewDrug(drug)"
          >
            <!-- 热门标记 -->
            <div v-if="drug.is_hot" class="hot-badge">热门</div>
            
            <!-- 医保标记 -->
            <div v-if="drug.medical_insurance" class="insurance-badge" :class="getInsuranceClass(drug.medical_insurance)">
              {{ drug.medical_insurance }}
            </div>
            
            <!-- 药品图片 -->
            <div class="drug-image-wrapper">
              <el-image
                :src="drug.drug_image || '/default-drug.png'"
                fit="cover"
                class="drug-image"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon :size="32"><FirstAidKit /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
            
            <!-- 药品信息 -->
            <div class="drug-info">
              <h4 class="drug-name">{{ drug.trade_name || drug.drug_name }}</h4>
              <p v-if="drug.trade_name" class="drug-subname">{{ drug.drug_name }}</p>
              
              <div class="drug-tags">
                <el-tag v-if="drug.dosage_form" type="info" size="small" effect="plain">
                  {{ drug.dosage_form }}
                </el-tag>
              </div>
              
              <p class="drug-spec">{{ drug.specification || '暂无规格' }}</p>
              
              <p class="drug-manufacturer">{{ drug.manufacturer_name || '厂商未知' }}</p>
            </div>
            
            <!-- 操作按钮 -->
            <div class="drug-actions" @click.stop>
              <el-button 
                type="primary" 
                size="small" 
                circle
                @click="handleViewDrug(drug)"
                title="查看详情"
              >
                <el-icon><View /></el-icon>
              </el-button>
              <el-button 
                type="success" 
                size="small" 
                circle
                @click="handleAddToCabinet(drug)"
                title="加入药箱"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        
        <el-empty v-else description="暂无药品数据" />
      </div>

      <template #footer>
        <el-button @click="drugsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 药品详情对话框 -->
    <el-dialog v-model="drugDetailVisible" title="药品详情" width="800px" top="5vh" destroy-on-close>
      <div v-if="currentDrug" class="drug-detail">
        <div class="detail-header">
          <div class="detail-image">
            <el-image
              :src="currentDrug.drug_image || '/default-drug.png'"
              fit="cover"
              style="width: 100px; height: 100px; border-radius: 8px"
            >
              <template #error>
                <div class="image-placeholder-large">
                  <el-icon :size="40"><FirstAidKit /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
          <div class="detail-title">
            <h3>{{ currentDrug.trade_name || currentDrug.drug_name }}</h3>
            <p v-if="currentDrug.trade_name" class="subtitle">{{ currentDrug.drug_name }}</p>
            <div class="detail-tags">
              <el-tag v-if="currentDrug.is_hot" type="danger" size="small" effect="dark">热门</el-tag>
              <el-tag v-if="currentDrug.medical_insurance" :type="getInsuranceType(currentDrug.medical_insurance)" size="small">
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
        </el-descriptions>

        <div v-if="currentDrug.indications" class="detail-section">
          <h4><el-icon><FirstAidKit /></el-icon> 适用症状</h4>
          <p>{{ currentDrug.indications }}</p>
        </div>

        <div v-if="currentDrug.description" class="detail-section">
          <h4><el-icon><Document /></el-icon> 药品说明</h4>
          <p class="description-text">{{ currentDrug.description }}</p>
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
        <el-button @click="drugDetailVisible = false">关闭</el-button>
        <el-button type="success" @click="handleAddToCabinet(currentDrug); drugDetailVisible = false;">
          <el-icon><Box /></el-icon> 加入药箱
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加到药箱对话框 -->
    <el-dialog v-model="addToCabinetDialogVisible" title="添加药品到药箱" width="600px" top="10vh" destroy-on-close>
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
        <el-form-item label="有效期至">
          <el-date-picker v-model="addToCabinetForm.valid_until" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="addToCabinetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAddToCabinetSubmit">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'
import {
  ArrowRight, Folder, FirstAidKit, View, Plus, Box, Document,
  // 医学相关图标
  FirstAidKit as IconMedicine,
  // 系统功能图标
  Collection, Box as IconBox, FolderOpened
} from '@element-plus/icons-vue'

// 分类数据
const type1List = ref<any[]>([])
const type2List = ref<any[]>([])
const loading1 = ref(false)
const loading2 = ref(false)

// 对话框控制
const dialogVisible = ref(false)
const drugsDialogVisible = ref(false)
const drugDetailVisible = ref(false)
const addToCabinetDialogVisible = ref(false)
const selectedType1 = ref<any>(null)
const selectedType2Name = ref('')

// 药品数据
const categoryDrugs = ref<any[]>([])
const drugsLoading = ref(false)
const currentDrug = ref<any>(null)

// 添加到药箱
const addToCabinetForm = ref({
  cabinet: null as number | null,
  quantity: 1,
  unit: '',
  valid_until: ''
})
const cabinetOptions = ref<any[]>([])
const submitting = ref(false)

// 图标映射
const iconMap: Record<string, any> = {
  '抗感染': FirstAidKit,
  '呼吸': Collection,
  '消化': Folder,
  '皮肤': IconBox,
  '心血管': FolderOpened,
  '骨骼': IconMedicine,
  '感觉': Collection,
  '抗生素': FirstAidKit,
  'default': Folder
}

// 颜色配置 - 医疗相关配色
const colorList = [
  { bg: '#e8f4f8', icon: '#0891b2' },  // 青色
  { bg: '#f0fdf4', icon: '#16a34a' },  // 绿色
  { bg: '#fff7ed', icon: '#ea580c' },  // 橙色
  { bg: '#fef2f2', icon: '#dc2626' },  // 红色
  { bg: '#f5f3ff', icon: '#7c3aed' },  // 紫色
  { bg: '#fff1f2', icon: '#e11d48' },  // 粉色
  { bg: '#f0f9ff', icon: '#0284c7' },  // 蓝色
  { bg: '#f7fee7', icon: '#65a30d' },  // 黄绿色
  { bg: '#fffbeb', icon: '#d97706' },  // 琥珀色
  { bg: '#fdf4ff', icon: '#c026d3' }   // 紫红色
]

// 获取分类图标
const getCategoryIcon = (name: string) => {
  for (const key in iconMap) {
    if (name.includes(key)) {
      return iconMap[key]
    }
  }
  return iconMap['default']
}

// 获取图标样式
const getIconStyle = (id: number) => {
  const color = colorList[(id - 1) % colorList.length]
  return {
    backgroundColor: color.bg,
    color: color.icon
  }
}

// 获取分类描述
const getCategoryDesc = (name: string) => {
  const descMap: Record<string, string> = {
    '抗感染': '抗生素、抗病毒等抗感染药物',
    '呼吸': '治疗呼吸系统疾病的药物',
    '消化': '调节消化系统和代谢的药物',
    '皮肤': '治疗皮肤病的药物',
    '心血管': '心血管系统用药',
    '骨骼': '治疗肌肉骨骼系统疾病',
    '感觉': '眼科、耳鼻喉等感觉器官用药',
    '抗生素': '各类抗生素药物'
  }
  for (const key in descMap) {
    if (name.includes(key)) {
      return descMap[key]
    }
  }
  return '点击查看详情'
}

// 获取医保类型样式
const getInsuranceClass = (type: string) => {
  const map: Record<string, string> = {
    '甲类': 'type-a',
    '乙类': 'type-b',
    '非医保': 'type-none'
  }
  return map[type] || 'type-none'
}

// 获取医保类型
const getInsuranceType = (type: string) => {
  const map: Record<string, string> = {
    '甲类': 'danger',
    '乙类': 'warning',
    '非医保': 'info'
  }
  return map[type] || 'info'
}

// 获取一级分类
const fetchType1List = async () => {
  loading1.value = true
  try {
    const response = await api.get('/syyb/type1drug/')
    type1List.value = response.data.results || []
  } catch (error) {
    console.error('获取一级分类失败:', error)
  } finally {
    loading1.value = false
  }
}

// 获取二级分类
const fetchType2List = async (type1Id: number) => {
  loading2.value = true
  try {
    const response = await api.get(`/syyb/type1_type2/${type1Id}/`)
    type2List.value = response.data.results || []
  } catch (error) {
    console.error('获取二级分类失败:', error)
  } finally {
    loading2.value = false
  }
}

// 点击一级分类
const handleCategoryClick = (item: any) => {
  selectedType1.value = item
  dialogVisible.value = true
  fetchType2List(item.id)
}

// 查看分类下的药品
const viewDrugsByCategory = async (type2: any) => {
  selectedType2Name.value = type2.name
  drugsDialogVisible.value = true
  drugsLoading.value = true

  try {
    const response = await api.get(`/syyb/type2_drugs/${type2.id}/`)
    categoryDrugs.value = response.data.results || []
  } catch (error) {
    console.error('获取药品列表失败:', error)
  } finally {
    drugsLoading.value = false
  }
}

// 查看药品详情
const handleViewDrug = (row: any) => {
  currentDrug.value = row
  drugDetailVisible.value = true
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
      addToCabinetForm.value.cabinet = defaultCabinet.id
    }
  } catch (error) {
    console.error('获取药箱列表失败:', error)
  }
}

// 添加到药箱
const handleAddToCabinet = (row: any) => {
  currentDrug.value = row
  fetchCabinetOptions()
  addToCabinetForm.value = {
    cabinet: null,
    quantity: 1,
    unit: row.specification || '盒',
    valid_until: ''
  }
  addToCabinetDialogVisible.value = true
}

// 提交添加到药箱
const handleAddToCabinetSubmit = async () => {
  if (!currentDrug.value || !addToCabinetForm.value.cabinet) {
    ElMessage.warning('请选择药箱')
    return
  }

  submitting.value = true
  try {
    await api.post('/syyb/cabinet_drugs/', {
      cabinet: addToCabinetForm.value.cabinet,
      drug: currentDrug.value.id,
      quantity: addToCabinetForm.value.quantity,
      unit: addToCabinetForm.value.unit,
      valid_until: addToCabinetForm.value.valid_until
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
  fetchType1List()
})
</script>

<style scoped>
.category-browse-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-header p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 一级分类卡片网格 */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.category-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.category-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.category-card:hover .category-icon {
  transform: scale(1.1);
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-desc {
  font-size: 13px;
  color: #909399;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-arrow {
  color: #c0c4cc;
  transition: all 0.3s ease;
}

.category-card:hover .category-arrow {
  color: #409eff;
  transform: translateX(4px);
}

/* 二级分类对话框 */
.subcategory-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.subcategory-content {
  min-height: 200px;
}

.subcategory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.subcategory-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.subcategory-card:hover {
  background: #fff;
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.subcategory-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #409eff 0%, #79bbff 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.subcategory-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.subcategory-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.subcategory-arrow {
  color: #c0c4cc;
  opacity: 0;
  transition: all 0.3s ease;
}

.subcategory-card:hover .subcategory-arrow {
  opacity: 1;
  color: #409eff;
  transform: translateX(4px);
}

/* 药品卡片网格 - 新增样式 */
.drugs-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.drugs-content {
  min-height: 300px;
}

.drug-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.drug-card-item {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #ebeef5;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.drug-card-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

/* 标记 */
.hot-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #f56c6c 0%, #ff9a9e 100%);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  border-radius: 20px;
  z-index: 2;
}

.insurance-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 20px;
  z-index: 2;
}

.insurance-badge.type-a {
  background: #fef2f2;
  color: #dc2626;
}

.insurance-badge.type-b {
  background: #fffbeb;
  color: #d97706;
}

.insurance-badge.type-none {
  background: #f1f5f9;
  color: #64748b;
}

/* 药品图片 */
.drug-image-wrapper {
  width: 100%;
  height: 160px;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

.drug-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.drug-card-item:hover .drug-image {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #c0c4cc;
}

/* 药品信息 */
.drug-info {
  padding: 16px;
}

.drug-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.drug-subname {
  font-size: 12px;
  color: #909399;
  margin: 0 0 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-tags {
  margin-bottom: 10px;
}

.drug-spec {
  font-size: 13px;
  color: #606266;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-manufacturer {
  font-size: 12px;
  color: #909399;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 操作按钮 */
.drug-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  background: #f8f9fa;
}

/* 药品详情样式 */
.drug-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.detail-image {
  flex-shrink: 0;
}

.image-placeholder-large {
  width: 100px;
  height: 100px;
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

.detail-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
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

.detail-section h4 {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.detail-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.description-text {
  white-space: pre-wrap;
}

/* 响应式 */
@media (max-width: 768px) {
  .category-grid {
    grid-template-columns: 1fr;
  }

  .subcategory-grid {
    grid-template-columns: 1fr;
  }
  
  .drug-cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }
}
</style>
