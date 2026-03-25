<template>
  <div class="category-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>分类管理</h2>
      <p>管理药品的一级分类和二级分类</p>
    </div>

    <!-- 一级分类操作栏 -->
    <div class="batch-actions" v-if="type1List.length > 0">
      <el-checkbox
        v-model="isAllType1Selected"
        @change="handleSelectAllType1"
        size="large"
      >
        全选 ({{ selectedType1List.length }}/{{ type1List.length }})
      </el-checkbox>
      <el-button
        type="danger"
        :disabled="!selectedType1List.length"
        @click="handleBatchDeleteType1"
        size="small"
      >
        <el-icon><Delete /></el-icon>批量删除({{ selectedType1List.length }})
      </el-button>
    </div>

    <!-- 一级分类卡片网格 -->
    <div v-loading="loading1" class="category-grid">
      <div
        v-for="item in type1List"
        :key="item.id"
        class="category-card"
        :class="{ selected: isType1Selected(item) }"
        @click="handleCategoryClick(item)"
      >
        <div class="card-checkbox" @click.stop>
          <el-checkbox
            :model-value="isType1Selected(item)"
            @change="toggleType1Selection(item)"
            size="large"
          />
        </div>
        <div class="category-icon" :style="getIconStyle(item.id)">
          <el-icon :size="40"><component :is="getCategoryIcon(item.name)" /></el-icon>
        </div>
        <div class="category-info">
          <h3 class="category-name">{{ item.name }}</h3>
          <p class="category-desc">{{ getCategoryDesc(item.name) }}</p>
        </div>
        <div class="category-count">
          <el-tag type="info" size="small">{{ item.type2_count || 0 }} 个子分类</el-tag>
        </div>
        <div class="category-arrow">
          <el-icon :size="20"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 新增分类卡片 -->
      <div class="category-card add-card" @click="handleAddType1">
        <div class="add-icon">
          <el-icon :size="40"><Plus /></el-icon>
        </div>
        <div class="category-info">
          <h3 class="category-name">新增分类</h3>
          <p class="category-desc">点击添加新的一级分类</p>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-if="!loading1 && type1List.length === 0" description="暂无分类数据">
      <el-button type="primary" @click="handleAddType1">
        <el-icon><Plus /></el-icon>添加分类
      </el-button>
    </el-empty>

    <!-- 二级分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="selectedType1?.name + ' - 子分类管理'"
      width="1000px"
      top="5vh"
      destroy-on-close
      class="subcategory-dialog"
    >
      <div class="dialog-header-actions">
        <el-button type="primary" @click="handleAddType2">
          <el-icon><Plus /></el-icon>新增子分类
        </el-button>
      </div>

      <div v-loading="loading2" class="subcategory-content">
        <!-- 二级分类批量操作 -->
        <div class="batch-actions" v-if="type2List.length > 0">
          <el-button
            type="danger"
            :disabled="!selectedType2List.length"
            @click="handleBatchDeleteType2"
            size="small"
          >
            <el-icon><Delete /></el-icon>批量删除({{ selectedType2List.length }})
          </el-button>
        </div>

        <!-- 二级分类卡片网格 -->
        <div v-if="type2List.length > 0" class="type2-grid">
          <div
            v-for="item in type2List"
            :key="item.id"
            class="type2-card"
            @click="handleType2Click(item)"
          >
            <div class="type2-checkbox" @click.stop>
              <el-checkbox
                :model-value="isType2Selected(item)"
                @change="toggleType2Selection(item)"
                size="large"
              />
            </div>
            <div class="type2-icon" :style="getType2IconStyle(item.id)">
              <el-icon :size="32"><component :is="getCategoryIcon(item.name)" /></el-icon>
            </div>
            <div class="type2-info">
              <h4 class="type2-name">{{ item.name }}</h4>
              <p class="type2-desc">点击查看药品列表</p>
            </div>
            <div class="type2-count">
              <el-tag v-if="item.drugs_count > 0" type="primary" effect="light">
                {{ item.drugs_count }} 个药品
              </el-tag>
              <el-tag v-else type="info" size="small">暂无药品</el-tag>
            </div>
            <div class="type2-actions" @click.stop>
              <el-button type="primary" size="small" @click="handleEditType2(item)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" size="small" @click="handleDeleteType2(item)">
                <el-icon><Delete /></el-icon>
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

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 二级分类药品列表对话框 -->
    <el-dialog
      v-model="type2DrugsDialogVisible"
      :title="selectedType2?.name + ' - 药品列表'"
      width="1200px"
      top="5vh"
      destroy-on-close
      class="type2-drugs-dialog"
    >
      <div v-loading="loadingDrugs" class="type2-drugs-content">
        <!-- 药品卡片网格 -->
        <div v-if="type2Drugs.length > 0" class="drug-grid">
          <div
            v-for="drug in type2Drugs"
            :key="drug.id"
            class="drug-card"
          >
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
            </div>
          </div>
        </div>

        <el-empty v-else description="该分类下暂无药品">
          <el-button type="primary" @click="goToDrugList">
            <el-icon><Plus /></el-icon>添加药品
          </el-button>
        </el-empty>
      </div>

      <template #footer>
        <el-button @click="type2DrugsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑一级分类对话框 -->
    <el-dialog
      v-model="type1DialogVisible"
      :title="isEditType1 ? '编辑一级分类' : '新增一级分类'"
      width="500px"
      destroy-on-close
    >
      <el-form ref="type1FormRef" :model="type1Form" :rules="type1Rules" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="type1Form.name" placeholder="请输入分类名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="type1DialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitType1">
          {{ isEditType1 ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑二级分类对话框 -->
    <el-dialog
      v-model="type2DialogVisible"
      :title="isEditType2 ? '编辑二级分类' : '新增二级分类'"
      width="500px"
      destroy-on-close
    >
      <el-form ref="type2FormRef" :model="type2Form" :rules="type2Rules" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="type2Form.name" placeholder="请输入分类名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="type2DialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitType2">
          {{ isEditType2 ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  ArrowRight, Folder, Collection, Plus, Edit, Delete,
  FirstAidKit, Box, OfficeBuilding
} from '@element-plus/icons-vue'

// 分类数据
const type1List = ref<any[]>([])
const type2List = ref<any[]>([])
const loading1 = ref(false)
const loading2 = ref(false)
const selectedType1 = ref<any>(null)
const selectedType2 = ref<any>(null)

// 批量选择数据
const selectedType1List = ref<any[]>([])
const selectedType2List = ref<any[]>([])

// 对话框控制
const dialogVisible = ref(false)
const type1DialogVisible = ref(false)
const type2DialogVisible = ref(false)
const isEditType1 = ref(false)
const isEditType2 = ref(false)
const submitting = ref(false)

// 二级分类药品对话框
const type2DrugsDialogVisible = ref(false)
const type2Drugs = ref<any[]>([])
const loadingDrugs = ref(false)

// 表单
const type1FormRef = ref<FormInstance>()
const type2FormRef = ref<FormInstance>()
const type1Form = ref({ id: null as number | null, name: '' })
const type2Form = ref({ id: null as number | null, name: '' })

const type1Rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}
const type2Rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

// 图标映射
const iconMap: Record<string, any> = {
  '抗感染': FirstAidKit,
  '呼吸': Collection,
  '消化': Folder,
  '皮肤': Box,
  '心血管': OfficeBuilding,
  '骨骼': FirstAidKit,
  '感觉': Collection,
  '抗生素': FirstAidKit,
  'default': Folder
}

// 颜色配置
const colorList = [
  { bg: '#e8f4f8', icon: '#0891b2' },
  { bg: '#f0fdf4', icon: '#16a34a' },
  { bg: '#fff7ed', icon: '#ea580c' },
  { bg: '#fef2f2', icon: '#dc2626' },
  { bg: '#f5f3ff', icon: '#7c3aed' },
  { bg: '#fff1f2', icon: '#e11d48' },
  { bg: '#f0f9ff', icon: '#0284c7' },
  { bg: '#f7fee7', icon: '#65a30d' },
  { bg: '#fffbeb', icon: '#d97706' },
  { bg: '#fdf4ff', icon: '#c026d3' }
]

const getCategoryIcon = (name: string) => {
  for (const key in iconMap) {
    if (name.includes(key)) return iconMap[key]
  }
  return iconMap['default']
}

const getIconStyle = (id: number) => {
  const color = colorList[(id - 1) % colorList.length] || colorList[0]
  return { backgroundColor: color.bg, color: color.icon }
}

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
    if (name.includes(key)) return descMap[key]
  }
  return '点击查看详情'
}

// 获取一级分类
const fetchType1List = async () => {
  loading1.value = true
  try {
    const response = await api.get('/syyb/type1drug/')
    // 后端已返回 type2_count，无需额外请求
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

// 点击二级分类 - 查看药品
const handleType2Click = (item: any) => {
  selectedType2.value = item
  type2DrugsDialogVisible.value = true
  fetchType2Drugs(item.id)
}

// 获取二级分类下的药品
const fetchType2Drugs = async (type2Id: number) => {
  loadingDrugs.value = true
  try {
    const response = await api.get(`/syyb/type2_drugs/${type2Id}/`)
    type2Drugs.value = response.data.results || []
  } catch (error) {
    console.error('获取药品列表失败:', error)
    type2Drugs.value = []
  } finally {
    loadingDrugs.value = false
  }
}

// 跳转到药品列表
const goToDrugList = () => {
  type2DrugsDialogVisible.value = false
  dialogVisible.value = false
  // 这里可以添加路由跳转逻辑
}

// 二级分类卡片样式
const getType2IconStyle = (id: number) => {
  const color = colorList[(id - 1) % colorList.length] || colorList[0]
  return { backgroundColor: color.bg, color: color.icon }
}

// 是否选中二级分类
const isType2Selected = (item: any) => {
  return selectedType2List.value.some(i => i.id === item.id)
}

// 切换二级分类选中状态
const toggleType2Selection = (item: any) => {
  const index = selectedType2List.value.findIndex(i => i.id === item.id)
  if (index > -1) {
    selectedType2List.value.splice(index, 1)
  } else {
    selectedType2List.value.push(item)
  }
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

// 获取市场状态标签样式
const getMarketStatusType = (status: string) => {
  const map: Record<string, string> = {
    '在售': 'success',
    '停产': 'info',
    '退市': 'danger'
  }
  return map[status] || 'info'
}

// 新增一级分类
const handleAddType1 = () => {
  isEditType1.value = false
  type1Form.value = { id: null, name: '' }
  type1DialogVisible.value = true
}

// 编辑一级分类
const handleEditType1 = (item: any) => {
  isEditType1.value = true
  type1Form.value = { id: item.id, name: item.name }
  type1DialogVisible.value = true
}

// 删除一级分类
const handleDeleteType1 = (item: any) => {
  ElMessageBox.confirm(`确定要删除分类 "${item.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/type1drug/${item.id}/`)
      ElMessage.success('删除成功')
      fetchType1List()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

// 提交一级分类
const handleSubmitType1 = async () => {
  if (!type1FormRef.value) return
  await type1FormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEditType1.value && type1Form.value.id) {
          await api.put(`/syyb/type1drug/${type1Form.value.id}/`, { name: type1Form.value.name })
        } else {
          await api.post('/syyb/type1drug/', { name: type1Form.value.name })
        }
        ElMessage.success(isEditType1.value ? '更新成功' : '添加成功')
        type1DialogVisible.value = false
        fetchType1List()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 新增二级分类
const handleAddType2 = () => {
  if (!selectedType1.value) return
  isEditType2.value = false
  type2Form.value = { id: null, name: '' }
  type2DialogVisible.value = true
}

// 编辑二级分类
const handleEditType2 = (item: any) => {
  isEditType2.value = true
  type2Form.value = { id: item.id, name: item.name }
  type2DialogVisible.value = true
}

// 删除二级分类
const handleDeleteType2 = (item: any) => {
  ElMessageBox.confirm(`确定要删除分类 "${item.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/syyb/type2drug/${item.id}/`)
      ElMessage.success('删除成功')
      fetchType2List(selectedType1.value.id)
      fetchType1List() // 更新子分类数量
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

// 提交二级分类
const handleSubmitType2 = async () => {
  if (!type2FormRef.value || !selectedType1.value) return
  await type2FormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = {
          name: type2Form.value.name,
          type1_drug: selectedType1.value.id
        }
        if (isEditType2.value && type2Form.value.id) {
          await api.put(`/syyb/type2drug/${type2Form.value.id}/`, payload)
        } else {
          await api.post('/syyb/type2drug/', payload)
        }
        ElMessage.success(isEditType2.value ? '更新成功' : '添加成功')
        type2DialogVisible.value = false
        fetchType2List(selectedType1.value.id)
        fetchType1List() // 更新子分类数量
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  fetchType1List()
})

// ========== 一级分类批量操作 ==========

// 是否选中一级分类
const isType1Selected = (item: any) => {
  return selectedType1List.value.some(i => i.id === item.id)
}

// 切换一级分类选中状态
const toggleType1Selection = (item: any) => {
  const index = selectedType1List.value.findIndex(i => i.id === item.id)
  if (index > -1) {
    selectedType1List.value.splice(index, 1)
  } else {
    selectedType1List.value.push(item)
  }
}

// 是否全选一级分类
const isAllType1Selected = computed({
  get: () => type1List.value.length > 0 && selectedType1List.value.length === type1List.value.length,
  set: (val) => {
    if (val) {
      selectedType1List.value = [...type1List.value]
    } else {
      selectedType1List.value = []
    }
  }
})

// 全选/取消全选一级分类
const handleSelectAllType1 = () => {
  if (isAllType1Selected.value) {
    selectedType1List.value = []
  } else {
    selectedType1List.value = [...type1List.value]
  }
}

// 批量删除一级分类
const handleBatchDeleteType1 = () => {
  const names = selectedType1List.value.map(item => item.name).join('、')
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedType1List.value.length} 个一级分类吗？<br><small style="color: #909399;">包含：${names}</small>`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: true
    }
  ).then(async () => {
    try {
      const ids = selectedType1List.value.map(item => item.id)
      await api.delete('/syyb/type1drug/batch_delete/', { data: { ids } })
      ElMessage.success('批量删除成功')
      selectedType1List.value = []
      fetchType1List()
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  })
}

// ========== 二级分类批量操作 ==========

// 二级分类表格选择变化
const handleType2SelectionChange = (selection: any[]) => {
  selectedType2List.value = selection
}

// 批量删除二级分类
const handleBatchDeleteType2 = () => {
  const names = selectedType2List.value.map(item => item.name).join('、')
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedType2List.value.length} 个二级分类吗？<br><small style="color: #909399;">包含：${names}</small>`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: true
    }
  ).then(async () => {
    try {
      const ids = selectedType2List.value.map(item => item.id)
      await api.delete('/syyb/type2drug/batch_delete/', { data: { ids } })
      ElMessage.success('批量删除成功')
      selectedType2List.value = []
      fetchType2List(selectedType1.value.id)
      fetchType1List()
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  })
}
</script>

<style scoped>
.category-page {
  padding: 0;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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
  border: 2px solid transparent;
  position: relative;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.category-card.selected {
  border-color: #409eff;
  background: #f0f9ff;
}

.card-checkbox {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 10;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.category-card.add-card {
  border-style: dashed;
  background: #fafafa;
}

.category-card.add-card:hover {
  background: #f0f9ff;
  border-color: #409eff;
}

.add-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: #e6f2ff;
  color: #409eff;
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

.category-count {
  position: absolute;
  top: 16px;
  right: 40px;
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
.dialog-header-actions {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

.subcategory-content {
  min-height: 200px;
}

.empty-text {
  color: #c0c4cc;
}

/* 二级分类卡片网格 */
.type2-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.type2-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 2px solid transparent;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.type2-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.type2-checkbox {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 10;
}

.type2-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.type2-info {
  margin-bottom: 12px;
}

.type2-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.type2-desc {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.type2-count {
  margin-bottom: 12px;
}

.type2-actions {
  display: flex;
  gap: 8px;
}

/* 药品网格 */
.type2-drugs-content {
  min-height: 300px;
}

.type2-drugs-content .drug-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.type2-drugs-content .drug-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
}

.type2-drugs-content .drug-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.type2-drugs-content .drug-image-wrapper {
  height: 120px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.type2-drugs-content .drug-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.type2-drugs-content .image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.type2-drugs-content .drug-info {
  padding: 12px;
}

.type2-drugs-content .drug-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type2-drugs-content .drug-subtitle {
  font-size: 12px;
  color: #909399;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type2-drugs-content .drug-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.type2-drugs-content .drug-spec {
  font-size: 12px;
  color: #606266;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type2-drugs-content .drug-indications {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  font-size: 11px;
  color: #67c23a;
  line-height: 1.4;
}

.type2-drugs-content .drug-indications span {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 响应式 */
@media (max-width: 768px) {
  .category-grid {
    grid-template-columns: 1fr;
  }
}
</style>
