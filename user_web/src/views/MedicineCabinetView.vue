<template>
  <div class="cabinet-page">
    <!-- 页面标题和统计 -->
    <el-card class="stats-card" shadow="never">
      <div class="stats-header">
        <div class="stats-title">
          <h2>我的药箱</h2>
          <p>管理您的家庭药品，随时掌握药品有效期和库存情况</p>
        </div>
        <div class="stats-actions">
          <el-button type="primary" @click="handleAddCabinet">
            <el-icon><Plus /></el-icon>新建药箱
          </el-button>
        </div>
      </div>
      
      <el-row :gutter="20" class="stats-row">
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-icon blue">
              <el-icon :size="24"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.totalDrugs }}</p>
              <p class="stat-label">药品总数</p>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-icon green">
              <el-icon :size="24"><Check /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.validDrugs }}</p>
              <p class="stat-label">有效期内</p>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-icon warning">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.expiringSoon }}</p>
              <p class="stat-label">即将过期</p>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-icon danger">
              <el-icon :size="24"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.expired }}</p>
              <p class="stat-label">已过期</p>
            </div>
          </div>
        </el-col>
        
        <el-col :span="4">
          <div class="stat-box">
            <div class="stat-icon purple">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.lowStock }}</p>
              <p class="stat-label">库存不足</p>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 药箱列表 -->
    <el-row :gutter="20" class="cabinet-row">
      <el-col :span="6" v-for="cabinet in cabinets" :key="cabinet.id">
        <el-card 
          class="cabinet-card" 
          :class="{ active: selectedCabinet?.id === cabinet.id }"
          shadow="hover"
          @click="selectCabinet(cabinet)"
        >
          <div class="cabinet-header">
            <div class="cabinet-icon" :class="getCabinetIconClass(cabinet.cabinet_type)">
              <el-icon :size="28"><component :is="getCabinetIcon(cabinet.cabinet_type)" /></el-icon>
            </div>
            <div class="cabinet-info">
              <h4>{{ cabinet.name }}</h4>
              <p>{{ getCabinetTypeText(cabinet.cabinet_type) }}</p>
            </div>
            <el-tag v-if="cabinet.is_default" type="success" size="small">默认</el-tag>
          </div>
          <div class="cabinet-stats">
            <span>{{ cabinet.drug_count || 0 }} 种药品</span>
          </div>
          <div class="cabinet-actions" @click.stop>
            <el-button link type="primary" size="small" @click="handleEditCabinet(cabinet)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button link type="danger" size="small" @click="handleDeleteCabinet(cabinet)" :disabled="cabinet.is_default">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 药品列表 -->
    <el-card class="drug-list-card" shadow="never" v-if="selectedCabinet">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">{{ selectedCabinet.name }}</span>
            <el-radio-group v-model="filterType" size="small" @change="handleFilterChange">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="valid">有效期内</el-radio-button>
              <el-radio-button label="expiring_soon">即将过期</el-radio-button>
              <el-radio-button label="expired">已过期</el-radio-button>
              <el-radio-button label="low_stock">库存不足</el-radio-button>
            </el-radio-group>
          </div>
          <div class="header-actions">
            <el-button type="success" size="small" @click="showScanDialog">
              <el-icon><Camera /></el-icon>扫码录入
            </el-button>
            <el-button type="primary" size="small" @click="showAddDrugDialog">
              <el-icon><Plus /></el-icon>添加药品
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="cabinetDrugs" v-loading="loading" stripe border>
        <el-table-column label="药品信息" min-width="200">
          <template #default="{ row }">
            <div class="drug-info">
              <el-image
                :src="row.drug_image || '/default-drug.png'"
                fit="cover"
                style="width: 50px; height: 50px; border-radius: 4px"
              >
                <template #error>
                  <div class="image-placeholder-small">
                    <el-icon><FirstAidKit /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="drug-text">
                <p class="drug-name">{{ row.drug_name }}</p>
                <p class="drug-spec">{{ row.drug_specification || '-' }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="库存" width="140" align="center">
          <template #default="{ row }">
            <div class="quantity-control">
              <el-button link size="small" @click="updateQuantity(row, 'decrease')">
                <el-icon><Minus /></el-icon>
              </el-button>
              <span :class="['quantity', { 'low-stock': row.quantity <= 2 }]">
                {{ row.quantity }}{{ row.unit || '件' }}
                <el-icon v-if="row.quantity <= 2" class="warning-icon"><Warning /></el-icon>
              </span>
              <el-button link size="small" @click="updateQuantity(row, 'increase')">
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="批号" prop="batch_number" width="120" />
        
        <el-table-column label="生产日期" width="110">
          <template #default="{ row }">
            {{ row.production_date || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="有效期至" width="110">
          <template #default="{ row }">
            <span :class="getExpiryClass(row)">{{ row.valid_until || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getExpiryTagType(row)" size="small">
              {{ getExpiryText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEditDrug(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button link type="danger" size="small" @click="handleDeleteDrug(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 空状态 -->
      <el-empty v-if="!cabinetDrugs.length && !loading" description="暂无药品">
        <el-button type="primary" @click="showAddDrugDialog">添加药品</el-button>
      </el-empty>
    </el-card>
    
    <!-- 空状态（未选择药箱时） -->
    <el-card class="empty-card" shadow="never" v-else>
      <el-empty description="请选择或创建一个药箱">
        <el-button type="primary" @click="handleAddCabinet">创建药箱</el-button>
      </el-empty>
    </el-card>
    
    <!-- 添加/编辑药箱对话框 -->
    <el-dialog v-model="cabinetDialogVisible" :title="isEditCabinet ? '编辑药箱' : '新建药箱'" width="500px" destroy-on-close>
      <el-form ref="cabinetFormRef" :model="cabinetForm" :rules="cabinetRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="cabinetForm.name" placeholder="请输入药箱名称" />
        </el-form-item>
        <el-form-item label="类型" prop="cabinet_type">
          <el-select v-model="cabinetForm.cabinet_type" placeholder="选择类型" style="width: 100%">
            <el-option label="家庭药箱" value="home" />
            <el-option label="旅行药箱" value="travel" />
            <el-option label="办公室药箱" value="office" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="cabinetForm.is_default" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="cabinetForm.description" type="textarea" rows="3" placeholder="请输入药箱描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cabinetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCabinetSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加药品对话框 -->
    <el-dialog v-model="addDrugDialogVisible" title="添加药品到药箱" width="600px" destroy-on-close>
      <el-form ref="addDrugFormRef" :model="addDrugForm" :rules="addDrugRules" label-width="100px">
        <el-form-item label="选择药品" prop="drug">
          <el-select
            v-model="addDrugForm.drug"
            placeholder="搜索并选择药品"
            filterable
            remote
            :remote-method="searchDrugs"
            :loading="searching"
            style="width: 100%"
          >
            <el-option
              v-for="item in drugOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="addDrugForm.quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="addDrugForm.unit" placeholder="如：片、粒、瓶" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产日期">
              <el-date-picker v-model="addDrugForm.production_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至">
              <el-date-picker v-model="addDrugForm.valid_until" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="批号">
          <el-input v-model="addDrugForm.batch_number" placeholder="请输入批号" />
        </el-form-item>
        <el-form-item label="提醒天数">
          <el-input-number v-model="addDrugForm.remind_before_days" :min="1" :max="365" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="addDrugForm.notes" type="textarea" rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDrugDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAddDrugSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 扫码录入对话框 -->
    <el-dialog v-model="scanDialogVisible" title="扫码录入药品" width="550px" destroy-on-close>
      <div class="scan-container">
        <!-- 扫码步骤条 -->
        <el-steps :active="scanStep" simple>
          <el-step title="扫描/搜索" />
          <el-step title="确认信息" />
          <el-step title="添加到药箱" />
        </el-steps>
        
        <!-- 步骤1: 扫描或搜索 -->
        <div v-if="scanStep === 0" class="scan-step">
          <div class="scan-simulation">
            <div class="scan-area" @click="simulateScan">
              <el-icon :size="48" color="#409EFF"><Camera /></el-icon>
              <p>点击模拟扫码</p>
              <span class="scan-hint">或输入药品名称/批准文号搜索</span>
            </div>
          </div>
          
          <el-divider>或</el-divider>
          
          <el-form>
            <el-form-item>
              <el-input
                v-model="scanSearchQuery"
                placeholder="输入药品名称搜索"
                clearable
                @keyup.enter="searchDrugsForScan"
              >
                <template #append>
                  <el-button @click="searchDrugsForScan">
                    <el-icon><Search /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
          
          <!-- 搜索结果 -->
          <div v-if="scanSearchResults.length > 0" class="scan-results">
            <p class="results-title">搜索结果：</p>
            <el-scrollbar height="200px">
              <div
                v-for="drug in scanSearchResults"
                :key="drug.id"
                class="scan-drug-item"
                @click="selectScannedDrug(drug)"
              >
                <el-image
                  :src="drug.drug_image || '/default-drug.png'"
                  fit="cover"
                  style="width: 50px; height: 50px; border-radius: 4px"
                />
                <div class="scan-drug-info">
                  <p class="scan-drug-name">{{ drug.trade_name || drug.drug_name }}</p>
                  <p class="scan-drug-spec">{{ drug.specification || '暂无规格' }}</p>
                  <p class="scan-drug-manufacturer">{{ drug.manufacturer_name || '-' }}</p>
                </div>
                <el-button type="primary" size="small">选择</el-button>
              </div>
            </el-scrollbar>
          </div>
          
          <div v-else-if="scanSearched && scanSearchResults.length === 0" class="scan-empty">
            <el-empty description="未找到相关药品" />
          </div>
        </div>
        
        <!-- 步骤2: 确认信息 -->
        <div v-else-if="scanStep === 1" class="scan-step">
          <div class="scan-confirm">
            <el-image
              :src="scannedDrug.drug_image || '/default-drug.png'"
              fit="cover"
              style="width: 100px; height: 100px; border-radius: 8px; margin-bottom: 16px"
            />
            <h4>{{ scannedDrug.trade_name || scannedDrug.drug_name }}</h4>
            <p class="confirm-spec">{{ scannedDrug.specification || '暂无规格' }}</p>
            <p class="confirm-manufacturer">{{ scannedDrug.manufacturer_name || '-' }}</p>
            
            <el-divider />
            
            <el-form label-width="100px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="数量">
                    <el-input-number v-model="scanAddForm.quantity" :min="1" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="单位">
                    <el-input v-model="scanAddForm.unit" placeholder="如：片、粒、瓶" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="生产日期">
                    <el-date-picker v-model="scanAddForm.production_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="有效期至">
                    <el-date-picker v-model="scanAddForm.valid_until" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="批号">
                <el-input v-model="scanAddForm.batch_number" placeholder="请输入批号" />
              </el-form-item>
              <el-form-item label="提醒天数">
                <el-input-number v-model="scanAddForm.remind_before_days" :min="1" :max="365" style="width: 100%" />
              </el-form-item>
            </el-form>
          </div>
        </div>
        
        <!-- 步骤3: 完成 -->
        <div v-else-if="scanStep === 2" class="scan-step">
          <div class="scan-success">
            <el-icon :size="64" color="#67C23A"><CircleCheck /></el-icon>
            <h4>添加成功！</h4>
            <p>药品已成功添加到 {{ selectedCabinet?.name }}</p>
            <el-button type="primary" @click="closeScanDialog">完成</el-button>
            <el-button link @click="scanStep = 0">继续添加</el-button>
          </div>
        </div>
      </div>
      
      <template #footer v-if="scanStep === 1">
        <el-button @click="scanStep = 0">上一步</el-button>
        <el-button type="primary" :loading="submitting" @click="submitScannedDrug">添加到药箱</el-button>
      </template>
      <template #footer v-else-if="scanStep === 0">
        <el-button @click="scanDialogVisible = false">取消</el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑药品对话框 -->
    <el-dialog v-model="editDrugDialogVisible" title="编辑药品信息" width="600px" destroy-on-close>
      <el-form ref="editDrugFormRef" :model="editDrugForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量">
              <el-input-number v-model="editDrugForm.quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="editDrugForm.unit" placeholder="如：片、粒、瓶" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产日期">
              <el-date-picker v-model="editDrugForm.production_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至">
              <el-date-picker v-model="editDrugForm.valid_until" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="批号">
          <el-input v-model="editDrugForm.batch_number" placeholder="请输入批号" />
        </el-form-item>
        <el-form-item label="提醒天数">
          <el-input-number v-model="editDrugForm.remind_before_days" :min="1" :max="365" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editDrugForm.notes" type="textarea" rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDrugDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEditDrugSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus, Edit, Delete, Box, Check, Warning, CircleClose,
  FirstAidKit, HomeFilled, Suitcase, OfficeBuilding, Folder,
  Minus, Camera, Search
} from '@element-plus/icons-vue'

// 统计数据
const stats = reactive({
  totalDrugs: 0,
  validDrugs: 0,
  expiringSoon: 0,
  expired: 0,
  lowStock: 0
})

// 药箱列表
const cabinets = ref<any[]>([])
const selectedCabinet = ref<any>(null)
const loading = ref(false)

// 药品列表
const cabinetDrugs = ref<any[]>([])
const filterType = ref('all')

// 药箱对话框
const cabinetDialogVisible = ref(false)
const isEditCabinet = ref(false)
const cabinetFormRef = ref<FormInstance>()
const cabinetForm = reactive({
  id: null as number | null,
  name: '',
  cabinet_type: 'home',
  is_default: false,
  description: ''
})
const cabinetRules: FormRules = {
  name: [{ required: true, message: '请输入药箱名称', trigger: 'blur' }],
  cabinet_type: [{ required: true, message: '请选择药箱类型', trigger: 'change' }]
}

// 添加药品对话框
const addDrugDialogVisible = ref(false)
const addDrugFormRef = ref<FormInstance>()
const addDrugForm = reactive({
  cabinet: null as number | null,
  drug: null as number | null,
  quantity: 1,
  unit: '',
  production_date: '',
  valid_until: '',
  batch_number: '',
  remind_before_days: 7,
  notes: ''
})
const addDrugRules: FormRules = {
  drug: [{ required: true, message: '请选择药品', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}
const drugOptions = ref<any[]>([])
const searching = ref(false)

// 编辑药品对话框
const editDrugDialogVisible = ref(false)
const editDrugForm = reactive({
  id: null as number | null,
  quantity: 1,
  unit: '',
  production_date: '',
  valid_until: '',
  batch_number: '',
  remind_before_days: 7,
  notes: ''
})

// 扫码录入相关
const scanDialogVisible = ref(false)
const scanStep = ref(0)
const scanSearchQuery = ref('')
const scanSearchResults = ref<any[]>([])
const scanSearched = ref(false)
const scannedDrug = ref<any>(null)
const scanAddForm = reactive({
  cabinet: null as number | null,
  drug: null as number | null,
  quantity: 1,
  unit: '',
  production_date: '',
  valid_until: '',
  batch_number: '',
  remind_before_days: 7,
  notes: ''
})

// 显示扫码对话框
const showScanDialog = () => {
  if (!selectedCabinet.value) {
    ElMessage.warning('请先选择一个药箱')
    return
  }
  scanStep.value = 0
  scanSearchQuery.value = ''
  scanSearchResults.value = []
  scanSearched.value = false
  scannedDrug.value = null
  scanDialogVisible.value = true
}

// 模拟扫码
const simulateScan = () => {
  ElMessage.info('正在模拟扫码...')
  setTimeout(() => {
    // 随机搜索一些药品
    searchDrugsForScan('感冒')
    ElMessage.success('扫描成功，请从列表中选择药品')
  }, 800)
}

// 搜索药品用于扫码
const searchDrugsForScan = async (query?: string) => {
  const searchText = query || scanSearchQuery.value
  if (!searchText) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  scanSearched.value = true
  try {
    const response = await api.post('/syyb/search_anything/', { text: searchText })
    const drugs = response.data.results || []
    scanSearchResults.value = drugs.slice(0, 10) // 最多显示10个结果
  } catch (error) {
    console.error('搜索药品失败:', error)
    ElMessage.error('搜索失败')
  }
}

// 选择扫码结果中的药品
const selectScannedDrug = (drug: any) => {
  scannedDrug.value = drug
  scanAddForm.drug = drug.id
  scanAddForm.cabinet = selectedCabinet.value?.id
  scanAddForm.quantity = 1
  scanAddForm.unit = ''
  scanAddForm.production_date = ''
  scanAddForm.valid_until = ''
  scanAddForm.batch_number = ''
  scanAddForm.remind_before_days = 7
  scanAddForm.notes = ''
  scanStep.value = 1
}

// 提交扫码添加的药品
const submitScannedDrug = async () => {
  if (!scanAddForm.drug || !scanAddForm.cabinet) {
    ElMessage.error('药品信息不完整')
    return
  }
  
  submitting.value = true
  try {
    await api.post('/syyb/cabinet_drugs/', scanAddForm)
    scanStep.value = 2
    fetchCabinetDrugs()
    fetchStats()
  } catch (error) {
    console.error('添加失败:', error)
    ElMessage.error('添加药品失败')
  } finally {
    submitting.value = false
  }
}

// 关闭扫码对话框
const closeScanDialog = () => {
  scanDialogVisible.value = false
  scanStep.value = 0
}

const submitting = ref(false)

// 获取药箱类型图标
const getCabinetIcon = (type: string) => {
  const icons: Record<string, any> = {
    home: HomeFilled,
    travel: Suitcase,
    office: OfficeBuilding,
    other: Folder
  }
  return icons[type] || Box
}

const getCabinetIconClass = (type: string) => {
  const classes: Record<string, string> = {
    home: 'blue',
    travel: 'green',
    office: 'orange',
    other: 'purple'
  }
  return classes[type] || 'blue'
}

const getCabinetTypeText = (type: string) => {
  const texts: Record<string, string> = {
    home: '家庭药箱',
    travel: '旅行药箱',
    office: '办公室药箱',
    other: '其他'
  }
  return texts[type] || '其他'
}

// 获取药箱列表
const fetchCabinets = async () => {
  try {
    const response = await api.get('/syyb/cabinets/')
    cabinets.value = response.data.results || []
    
    // 自动选择默认药箱或第一个药箱
    if (cabinets.value.length && !selectedCabinet.value) {
      const defaultCabinet = cabinets.value.find((c: any) => c.is_default)
      selectCabinet(defaultCabinet || cabinets.value[0])
    }
    
    // 更新统计数据
    fetchStats()
  } catch (error) {
    console.error('获取药箱列表失败:', error)
  }
}

// 获取药箱药品
const fetchCabinetDrugs = async () => {
  if (!selectedCabinet.value) return
  
  loading.value = true
  try {
    const response = await api.get(`/syyb/cabinets/${selectedCabinet.value.id}/drugs/`, {
      params: { filter: filterType.value }
    })
    cabinetDrugs.value = response.data.results || []
    // 获取药品后更新统计
    fetchStats()
  } catch (error) {
    console.error('获取药品列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取过期统计
const fetchExpiringStats = async () => {
  try {
    const response = await api.get('/syyb/expiring_drugs/')
    const data = response.data
    stats.expiringSoon = data.expiring_soon_count || 0
    stats.expired = data.expired_count || 0
    // 如果有总数据，同步更新总数
    if (data.total_count !== undefined) {
      stats.totalDrugs = data.total_count
    }
    if (data.valid_count !== undefined) {
      stats.validDrugs = data.valid_count
    }
  } catch (error) {
    console.error('获取过期统计失败:', error)
  }
}

// 选择药箱
const selectCabinet = (cabinet: any) => {
  selectedCabinet.value = cabinet
  fetchCabinetDrugs()
}

// 筛选变化
const handleFilterChange = () => {
  fetchCabinetDrugs()
}

// 获取过期状态样式
const getExpiryClass = (row: any) => {
  if (row.is_expired) return 'expired'
  if (row.is_expiring_soon) return 'expiring-soon'
  return ''
}

const getExpiryTagType = (row: any) => {
  if (row.is_expired) return 'danger'
  if (row.is_expiring_soon) return 'warning'
  return 'success'
}

const getExpiryText = (row: any) => {
  if (row.is_expired) return '已过期'
  if (row.is_expiring_soon) return `${row.days_until_expiry}天后过期`
  return '正常'
}

// 更新数量
const updateQuantity = async (row: any, action: string) => {
  try {
    await api.post(`/syyb/cabinet_drugs/${row.id}/quantity/`, {
      action,
      amount: 1
    })
    fetchCabinetDrugs()
    fetchStats()
  } catch (error) {
    console.error('更新数量失败:', error)
  }
}

// 新建药箱
const handleAddCabinet = () => {
  isEditCabinet.value = false
  Object.assign(cabinetForm, {
    id: null,
    name: '',
    cabinet_type: 'home',
    is_default: false,
    description: ''
  })
  cabinetDialogVisible.value = true
}

// 编辑药箱
const handleEditCabinet = (cabinet: any) => {
  isEditCabinet.value = true
  Object.assign(cabinetForm, cabinet)
  cabinetDialogVisible.value = true
}

// 删除药箱
const handleDeleteCabinet = (cabinet: any) => {
  ElMessageBox.confirm(`确定要删除药箱 "${cabinet.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/cabinets/${cabinet.id}/`)
      ElMessage.success('删除成功')
      if (selectedCabinet.value?.id === cabinet.id) {
        selectedCabinet.value = null
      }
      fetchCabinets()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

// 提交药箱表单
const handleCabinetSubmit = async () => {
  if (!cabinetFormRef.value) return
  
  await cabinetFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEditCabinet.value && cabinetForm.id) {
          await api.put(`/syyb/cabinets/${cabinetForm.id}/`, cabinetForm)
          ElMessage.success('更新成功')
        } else {
          await api.post('/syyb/cabinets/', cabinetForm)
          ElMessage.success('创建成功')
        }
        cabinetDialogVisible.value = false
        fetchCabinets()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 搜索药品
const searchDrugs = async (query: string) => {
  if (!query) return
  
  searching.value = true
  try {
    const response = await api.post('/syyb/search_anything/', { text: query })
    const drugs = response.data.results || []
    drugOptions.value = drugs.map((d: any) => ({
      id: d.id,
      name: `${d.trade_name || d.drug_name} (${d.specification || '无规格'})`
    }))
  } catch (error) {
    console.error('搜索药品失败:', error)
  } finally {
    searching.value = false
  }
}

// 显示添加药品对话框
const showAddDrugDialog = () => {
  if (!selectedCabinet.value) {
    ElMessage.warning('请先选择一个药箱')
    return
  }
  
  Object.assign(addDrugForm, {
    cabinet: selectedCabinet.value.id,
    drug: null,
    quantity: 1,
    unit: '',
    production_date: '',
    valid_until: '',
    batch_number: '',
    remind_before_days: 7,
    notes: ''
  })
  drugOptions.value = []
  addDrugDialogVisible.value = true
}

// 添加药品提交
const handleAddDrugSubmit = async () => {
  if (!addDrugFormRef.value) return
  
  await addDrugFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await api.post('/syyb/cabinet_drugs/', addDrugForm)
        ElMessage.success('添加成功')
        addDrugDialogVisible.value = false
        fetchCabinetDrugs()
        fetchStats()
      } catch (error) {
        console.error('添加失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 编辑药品
const handleEditDrug = (row: any) => {
  Object.assign(editDrugForm, {
    id: row.id,
    quantity: row.quantity,
    unit: row.unit,
    production_date: row.production_date,
    valid_until: row.valid_until,
    batch_number: row.batch_number,
    remind_before_days: row.remind_before_days,
    notes: row.notes
  })
  editDrugDialogVisible.value = true
}

// 编辑药品提交
const handleEditDrugSubmit = async () => {
  if (!editDrugForm.id) return
  
  submitting.value = true
  try {
    await api.patch(`/syyb/cabinet_drugs/${editDrugForm.id}/`, editDrugForm)
    ElMessage.success('更新成功')
    editDrugDialogVisible.value = false
    fetchCabinetDrugs()
    fetchStats()
  } catch (error) {
    console.error('更新失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除药品
const handleDeleteDrug = (row: any) => {
  ElMessageBox.confirm('确定要从此药箱中删除该药品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/cabinet_drugs/${row.id}/`)
      ElMessage.success('删除成功')
      fetchCabinetDrugs()
      fetchStats()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

// 更新统计数据
const fetchStats = async () => {
  if (selectedCabinet.value) {
    try {
      const response = await api.get(`/syyb/cabinets/${selectedCabinet.value.id}/drugs/`)
      const drugs = response.data.results || []
      stats.totalDrugs = drugs.length
      stats.validDrugs = drugs.filter((d: any) => !d.is_expired && !d.is_expiring_soon).length
    } catch (error) {
      console.error('获取统计失败:', error)
    }
  }
  fetchExpiringStats()
}

onMounted(() => {
  fetchCabinets()
})
</script>

<style scoped>
.cabinet-page {
  padding: 0;
}

.stats-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.stats-title h2 {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.stats-title p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.stats-actions .el-button {
  border-radius: 8px;
}

.stats-row {
  margin: 0;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #E6A23C 0%, #f3d19e 100%);
}

.stat-icon.danger {
  background: linear-gradient(135deg, #F56C6C 0%, #fab6b6 100%);
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

.cabinet-row {
  margin-bottom: 20px;
}

.cabinet-card {
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.cabinet-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.cabinet-card.active {
  border-color: #409EFF;
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

.cabinet-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.cabinet-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.cabinet-icon.blue {
  background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%);
}

.cabinet-icon.green {
  background: linear-gradient(135deg, #67C23A 0%, #95d475 100%);
}

.cabinet-icon.orange {
  background: linear-gradient(135deg, #E6A23C 0%, #f3d19e 100%);
}

.cabinet-icon.purple {
  background: linear-gradient(135deg, #8E44AD 0%, #bb8fce 100%);
}

.cabinet-info {
  flex: 1;
}

.cabinet-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.cabinet-info p {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.cabinet-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  font-size: 13px;
  color: #606266;
}

.cabinet-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.cabinet-card:hover .cabinet-actions {
  opacity: 1;
}

.drug-list-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.drug-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.image-placeholder-small {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 4px;
  color: #c0c4cc;
}

.drug-text {
  flex: 1;
}

.drug-name {
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.drug-spec {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.quantity-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.quantity {
  font-weight: 600;
  min-width: 40px;
  text-align: center;
}

.expired {
  color: #F56C6C;
  font-weight: 600;
}

.expiring-soon {
  color: #E6A23C;
  font-weight: 600;
}

/* 扫码录入样式 */
.scan-container {
  padding: 20px 0;
}

.scan-step {
  margin-top: 20px;
}

.scan-simulation {
  display: flex;
  justify-content: center;
  padding: 30px 0;
}

.scan-area {
  width: 200px;
  height: 200px;
  border: 2px dashed #409EFF;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f0f9ff;
}

.scan-area:hover {
  background: #e6f7ff;
  transform: scale(1.02);
}

.scan-area p {
  margin: 12px 0 4px 0;
  font-weight: 600;
  color: #409EFF;
}

.scan-hint {
  font-size: 12px;
  color: #909399;
}

.scan-results {
  margin-top: 16px;
}

.results-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.scan-drug-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 8px;
  border: 1px solid #ebeef5;
}

.scan-drug-item:hover {
  background: #f5f7fa;
  border-color: #409EFF;
}

.scan-drug-info {
  flex: 1;
}

.scan-drug-name {
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.scan-drug-spec {
  font-size: 13px;
  color: #606266;
  margin: 0 0 2px 0;
}

.scan-drug-manufacturer {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.scan-confirm {
  text-align: center;
  padding: 20px 0;
}

.scan-confirm h4 {
  font-size: 18px;
  color: #303133;
  margin: 0 0 8px 0;
}

.confirm-spec {
  color: #606266;
  margin: 0 0 4px 0;
}

.confirm-manufacturer {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.scan-success {
  text-align: center;
  padding: 40px 0;
}

.scan-success h4 {
  font-size: 20px;
  color: #67C23A;
  margin: 16px 0 8px 0;
}

.scan-success p {
  color: #606266;
  margin: 0 0 24px 0;
}

.scan-empty {
  padding: 20px 0;
}

.quantity.low-stock {
  color: #F56C6C;
  font-weight: 600;
}

.warning-icon {
  color: #F56C6C;
  margin-left: 4px;
  font-size: 14px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.empty-card {
  border-radius: 12px;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
