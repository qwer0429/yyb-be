<template>
  <div class="manufacturer-page">
    <div class="page-header">
      <h2>厂商管理</h2>
      <p>管理上市许可持有人和生产厂商信息</p>
    </div>

    <el-tabs v-model="activeTab" class="manufacturer-tabs" type="border-card">
      <el-tab-pane label="上市许可持有人" name="holder">
        <div class="tab-header">
          <span class="tab-desc">管理药品上市许可持有人信息</span>
          <div class="header-actions">
            <el-checkbox
              v-if="holderList.length > 0"
              v-model="isAllHolderSelected"
              @change="handleSelectAllHolder"
            >
              全选 ({{ selectedHolders.length }})
            </el-checkbox>
            <el-button
              type="danger"
              :disabled="!selectedHolders.length"
              @click="handleBatchDeleteHolder"
              size="small"
            >
              <el-icon><Delete /></el-icon>批量删除({{ selectedHolders.length }})
            </el-button>
            <el-button type="primary" @click="handleAddHolder">
              <el-icon><Plus /></el-icon>新增持有人
            </el-button>
          </div>
        </div>

        <div v-loading="loading1" class="manufacturer-grid">
          <div
            v-for="item in holderList"
            :key="item.id"
            class="manufacturer-card"
            :class="{ selected: isHolderSelected(item) }"
          >
            <div class="card-checkbox" @click.stop>
              <el-checkbox
                :model-value="isHolderSelected(item)"
                @change="toggleHolderSelection(item)"
              />
            </div>
            <div class="card-icon blue">
              <el-icon :size="32"><OfficeBuilding /></el-icon>
            </div>
            <div class="card-content">
              <h4 class="card-title" :title="item.name">{{ item.name }}</h4>
              <div class="card-meta-row">
                <el-tag v-if="item.abbreviation" type="info" size="small" effect="light" class="abbr-tag">{{ item.abbreviation }}</el-tag>
                <el-tag type="success" size="small" effect="dark" class="drug-count-tag">
                  <el-icon><FirstAidKit /></el-icon>
                  {{ item.drug_count || 0 }}个药品
                </el-tag>
              </div>
            </div>
            <div class="card-actions">
              <el-button type="success" text size="small" @click="handleViewHolderDrugs(item)" title="查看药品">
                <el-icon><View /></el-icon>
                <span class="action-text">药品</span>
              </el-button>
              <el-button type="primary" text size="small" @click="handleEditHolder(item)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" text size="small" @click="handleDeleteHolder(item)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>

          <div class="manufacturer-card add-card" @click="handleAddHolder">
            <div class="add-icon blue"><el-icon :size="32"><Plus /></el-icon></div>
            <div class="card-content">
              <h4 class="card-title">新增持有人</h4>
              <p class="card-desc">点击添加新的上市许可持有人</p>
            </div>
          </div>
        </div>

        <el-empty v-if="!loading1 && holderList.length === 0" description="暂无上市许可持有人数据">
          <el-button type="primary" @click="handleAddHolder"><el-icon><Plus /></el-icon>添加持有人</el-button>
        </el-empty>

        <!-- 持有人分页 -->
        <div class="pagination-wrapper" v-if="holderTotal > 0">
          <el-pagination
            v-model:current-page="holderPage"
            v-model:page-size="holderPageSize"
            :page-sizes="[30, 60, 90, 120]"
            :total="holderTotal"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleHolderSizeChange"
            @current-change="handleHolderPageChange"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="生产厂商" name="manufacturer">
        <div class="tab-header">
          <span class="tab-desc">管理药品生产厂商信息</span>
          <div class="header-actions">
            <el-checkbox
              v-if="manufacturerList.length > 0"
              v-model="isAllManufacturerSelected"
              @change="handleSelectAllManufacturer"
            >
              全选 ({{ selectedManufacturers.length }})
            </el-checkbox>
            <el-button
              type="danger"
              :disabled="!selectedManufacturers.length"
              @click="handleBatchDeleteManufacturer"
              size="small"
            >
              <el-icon><Delete /></el-icon>批量删除({{ selectedManufacturers.length }})
            </el-button>
            <el-button type="success" @click="handleAddManufacturer">
              <el-icon><Plus /></el-icon>新增厂商
            </el-button>
          </div>
        </div>

        <div v-loading="loading2" class="manufacturer-grid">
          <div
            v-for="item in manufacturerList"
            :key="item.id"
            class="manufacturer-card"
            :class="{ selected: isManufacturerSelected(item) }"
          >
            <div class="card-checkbox" @click.stop>
              <el-checkbox
                :model-value="isManufacturerSelected(item)"
                @change="toggleManufacturerSelection(item)"
              />
            </div>
            <div class="card-icon green"><el-icon :size="32"><Factory /></el-icon></div>
            <div class="card-content">
              <h4 class="card-title" :title="item.name">{{ item.name }}</h4>
              <div class="card-meta-row">
                <el-tag v-if="item.abbreviation" type="info" size="small" effect="light" class="abbr-tag">{{ item.abbreviation }}</el-tag>
                <el-tag type="success" size="small" effect="dark" class="drug-count-tag">
                  <el-icon><FirstAidKit /></el-icon>
                  {{ item.drug_count || 0 }}个药品
                </el-tag>
              </div>
            </div>
            <div class="card-actions">
              <el-button type="success" text size="small" @click="handleViewManufacturerDrugs(item)" title="查看药品">
                <el-icon><View /></el-icon>
                <span class="action-text">药品</span>
              </el-button>
              <el-button type="primary" text size="small" @click="handleEditManufacturer(item)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" text size="small" @click="handleDeleteManufacturer(item)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>

          <div class="manufacturer-card add-card" @click="handleAddManufacturer">
            <div class="add-icon green"><el-icon :size="32"><Plus /></el-icon></div>
            <div class="card-content">
              <h4 class="card-title">新增厂商</h4>
              <p class="card-desc">点击添加新的生产厂商</p>
            </div>
          </div>
        </div>

        <el-empty v-if="!loading2 && manufacturerList.length === 0" description="暂无生产厂商数据">
          <el-button type="success" @click="handleAddManufacturer"><el-icon><Plus /></el-icon>添加厂商</el-button>
        </el-empty>

        <!-- 厂商分页 -->
        <div class="pagination-wrapper" v-if="manufacturerTotal > 0">
          <el-pagination
            v-model:current-page="manufacturerPage"
            v-model:page-size="manufacturerPageSize"
            :page-sizes="[30, 60, 90, 120]"
            :total="manufacturerTotal"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleManufacturerSizeChange"
            @current-change="handleManufacturerPageChange"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" destroy-on-close align-center>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="全称" prop="name">
          <el-input v-model="form.name" placeholder="请输入全称" clearable maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="简称" prop="abbreviation">
          <el-input v-model="form.abbreviation" placeholder="请输入简称（可选）" clearable maxlength="20" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ isEdit ? '保存修改' : '立即创建' }}</el-button>
      </template>
    </el-dialog>

    <!-- 查看厂商/持有人药品对话框 -->
    <el-dialog
      v-model="drugsDialogVisible"
      :title="drugsDialogTitle"
      width="900px"
      destroy-on-close
      class="manufacturer-drugs-dialog"
    >
      <div v-loading="drugsLoading" class="drugs-container">
        <!-- 统计信息 -->
        <div class="drugs-stats">
          <el-tag type="primary" size="large" effect="dark">
            <el-icon><FirstAidKit /></el-icon>
            共 {{ manufacturerDrugs.length }} 个药品
          </el-tag>
        </div>

        <!-- 药品网格 -->
        <div v-if="manufacturerDrugs.length > 0" class="drugs-grid">
          <div
            v-for="drug in manufacturerDrugs"
            :key="drug.id"
            class="drug-item"
            @click="handleViewDrug(drug)"
          >
            <div class="drug-image-wrapper">
              <el-image
                :src="drug.drug_image || '/default-drug.png'"
                fit="cover"
                class="drug-image"
              >
                <template #error>
                  <div class="drug-image-placeholder">
                    <el-icon :size="32"><FirstAidKit /></el-icon>
                  </div>
                </template>
              </el-image>
              <div v-if="drug.is_hot" class="drug-hot-badge">热</div>
            </div>
            <div class="drug-content">
              <h4 class="drug-name" :title="drug.trade_name || drug.drug_name">{{ drug.trade_name || drug.drug_name }}</h4>
              <p v-if="drug.trade_name" class="drug-subname" :title="drug.drug_name">{{ drug.drug_name }}</p>
              <p class="drug-spec" :title="drug.specification">{{ drug.specification || '暂无规格' }}</p>
              <div class="drug-tags">
                <el-tag v-if="drug.medical_insurance" :type="getInsuranceType(drug.medical_insurance)" size="small">
                  {{ drug.medical_insurance }}
                </el-tag>
                <el-tag v-if="drug.dosage_form" type="info" size="small" effect="plain">
                  {{ drug.dosage_form }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty v-else description="暂无药品数据" />
      </div>
      <template #footer>
        <el-button @click="drugsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 药品详情对话框 -->
    <el-dialog
      v-model="drugDetailVisible"
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
                <div class="detail-image-placeholder">
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
          <el-descriptions-item label="批准文号">{{ currentDrug.approval_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="生产厂商">{{ currentDrug.manufacturer_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="上市许可持有人">{{ currentDrug.manufacturer_holder_name || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentDrug.indications" class="detail-section">
          <h4 class="section-title">
            <el-icon><FirstAidKit /></el-icon>
            适用症状
          </h4>
          <div class="section-content">{{ currentDrug.indications }}</div>
        </div>

        <div v-if="currentDrug.description" class="detail-section">
          <h4 class="section-title">药品说明</h4>
          <div class="section-content description-text">{{ currentDrug.description }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="drugDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { Plus, Edit, Delete, OfficeBuilding, OfficeBuilding as Factory, View, FirstAidKit } from '@element-plus/icons-vue';

const holderList = ref([]);
const manufacturerList = ref([]);
const loading1 = ref(false);
const loading2 = ref(false);
const activeTab = ref('holder');

// 分页数据
const holderPage = ref(1);
const holderPageSize = ref(30);
const holderTotal = ref(0);
const manufacturerPage = ref(1);
const manufacturerPageSize = ref(30);
const manufacturerTotal = ref(0);
const dialogVisible = ref(false);
const dialogType = ref<'holder' | 'manufacturer'>('holder');
const isEdit = ref(false);
const submitting = ref(false);
const formRef = ref<FormInstance>();
const form = reactive({ id: null as number | null, name: '', abbreviation: '' });
const rules: FormRules = { name: [{ required: true, message: '请输入全称', trigger: 'blur' }] };

// 批量选择数据
const selectedHolders = ref<any[]>([]);
const selectedManufacturers = ref<any[]>([]);

// 查看药品相关
const drugsDialogVisible = ref(false);
const drugsLoading = ref(false);
const manufacturerDrugs = ref<any[]>([]);
const currentManufacturer = ref<any>(null);
const currentViewType = ref<'holder' | 'manufacturer'>('manufacturer');
const drugsDialogTitle = computed(() => {
  const typeText = currentViewType.value === 'holder' ? '上市许可持有人' : '生产厂商';
  return `${currentManufacturer.value?.name || ''} - 药品列表`;
});

// 药品详情
const drugDetailVisible = ref(false);
const currentDrug = ref<any>(null);

// 上市许可持有人批量操作
const isHolderSelected = (item: any) => selectedHolders.value.some(h => h.id === item.id);
const toggleHolderSelection = (item: any) => {
  const index = selectedHolders.value.findIndex(h => h.id === item.id);
  if (index > -1) selectedHolders.value.splice(index, 1);
  else selectedHolders.value.push(item);
};
const isAllHolderSelected = computed({
  get: () => holderList.value.length > 0 && selectedHolders.value.length === holderList.value.length,
  set: (val) => {
    selectedHolders.value = val ? [...holderList.value] : [];
  }
});
const handleSelectAllHolder = () => {
  isAllHolderSelected.value = !isAllHolderSelected.value;
};
const handleBatchDeleteHolder = () => {
  const names = selectedHolders.value.map((h: any) => h.name).join('、');
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedHolders.value.length} 个上市许可持有人吗？<br><small style="color: #909399;">包含：${names}</small>`,
    '提示',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning', dangerouslyUseHTMLString: true }
  ).then(async () => {
    try {
      const ids = selectedHolders.value.map((h: any) => h.id);
      await api.delete('/syyb/manufacturerholder/batch_delete/', { data: { ids } });
      ElMessage.success('批量删除成功');
      selectedHolders.value = [];
      fetchHolderList();
    } catch (error) { ElMessage.error('批量删除失败'); }
  });
};

// 生产厂商批量操作
const isManufacturerSelected = (item: any) => selectedManufacturers.value.some(m => m.id === item.id);
const toggleManufacturerSelection = (item: any) => {
  const index = selectedManufacturers.value.findIndex(m => m.id === item.id);
  if (index > -1) selectedManufacturers.value.splice(index, 1);
  else selectedManufacturers.value.push(item);
};
const isAllManufacturerSelected = computed({
  get: () => manufacturerList.value.length > 0 && selectedManufacturers.value.length === manufacturerList.value.length,
  set: (val) => {
    selectedManufacturers.value = val ? [...manufacturerList.value] : [];
  }
});
const handleSelectAllManufacturer = () => {
  isAllManufacturerSelected.value = !isAllManufacturerSelected.value;
};
const handleBatchDeleteManufacturer = () => {
  const names = selectedManufacturers.value.map((m: any) => m.name).join('、');
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedManufacturers.value.length} 个生产厂商吗？<br><small style="color: #909399;">包含：${names}</small>`,
    '提示',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning', dangerouslyUseHTMLString: true }
  ).then(async () => {
    try {
      const ids = selectedManufacturers.value.map((m: any) => m.id);
      await api.delete('/syyb/manufacturer/batch_delete/', { data: { ids } });
      ElMessage.success('批量删除成功');
      selectedManufacturers.value = [];
      fetchManufacturerList();
    } catch (error) { ElMessage.error('批量删除失败'); }
  });
};

// 查看上市许可持有人的药品
const handleViewHolderDrugs = async (holder: any) => {
  currentManufacturer.value = holder;
  currentViewType.value = 'holder';
  drugsDialogVisible.value = true;
  drugsLoading.value = true;
  try {
    // 获取所有药品，然后在前端筛选（避免后端筛选参数不生效的问题）
    const response = await api.get('/syyb/drug/', {
      params: { page_size: 0 }
    });
    // 处理返回数据
    let drugsList = Array.isArray(response.data) ? response.data : (response.data.results || []);
    
    // 筛选属于该持有人的药品
    drugsList = drugsList.filter((drug: any) => {
      const holderId = drug.manufacturer_holder_id || drug.manufacturer_holder;
      return holderId === holder.id;
    });
    
    // 排序：有图片的在前，热门的在前
    drugsList.sort((a: any, b: any) => {
      const aHasImage = a.drug_image ? 1 : 0;
      const bHasImage = b.drug_image ? 1 : 0;
      if (aHasImage !== bHasImage) return bHasImage - aHasImage;
      const aIsHot = a.is_hot ? 1 : 0;
      const bIsHot = b.is_hot ? 1 : 0;
      if (aIsHot !== bIsHot) return bIsHot - aIsHot;
      return b.id - a.id;
    });
    manufacturerDrugs.value = drugsList;
  } catch (error) {
    console.error('获取药品列表失败:', error);
    ElMessage.error('获取药品列表失败');
  } finally {
    drugsLoading.value = false;
  }
};

// 查看生产厂商的药品
const handleViewManufacturerDrugs = async (manufacturer: any) => {
  currentManufacturer.value = manufacturer;
  currentViewType.value = 'manufacturer';
  drugsDialogVisible.value = true;
  drugsLoading.value = true;
  try {
    // 获取所有药品，然后在前端筛选（避免后端筛选参数不生效的问题）
    const response = await api.get('/syyb/drug/', {
      params: { page_size: 0 }
    });
    // 处理返回数据
    let drugsList = Array.isArray(response.data) ? response.data : (response.data.results || []);
    
    // 筛选属于该厂商的药品
    drugsList = drugsList.filter((drug: any) => {
      const manufacturerId = drug.manufacturer_id || drug.manufacturer;
      return manufacturerId === manufacturer.id;
    });
    
    // 排序：有图片的在前，热门的在前
    drugsList.sort((a: any, b: any) => {
      const aHasImage = a.drug_image ? 1 : 0;
      const bHasImage = b.drug_image ? 1 : 0;
      if (aHasImage !== bHasImage) return bHasImage - aHasImage;
      const aIsHot = a.is_hot ? 1 : 0;
      const bIsHot = b.is_hot ? 1 : 0;
      if (aIsHot !== bIsHot) return bIsHot - aIsHot;
      return b.id - a.id;
    });
    manufacturerDrugs.value = drugsList;
  } catch (error) {
    console.error('获取药品列表失败:', error);
    ElMessage.error('获取药品列表失败');
  } finally {
    drugsLoading.value = false;
  }
};

// 查看药品详情
const handleViewDrug = (drug: any) => {
  currentDrug.value = drug;
  drugDetailVisible.value = true;
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

const dialogTitle = computed(() => {
  const typeText = dialogType.value === 'holder' ? '上市许可持有人' : '生产厂商';
  return `${isEdit.value ? '编辑' : '新增'}${typeText}`;
});

const fetchHolderList = async () => {
  loading1.value = true;
  try {
    // 获取持有人列表
    const response = await api.get('/syyb/manufacturerholder/', {
      params: {
        page: holderPage.value,
        page_size: holderPageSize.value
      }
    });
    const holders = response.data.results || [];
    holderTotal.value = response.data.count || 0;
    
    // 获取所有药品，统计每个持有人的药品数量
    const drugResponse = await api.get('/syyb/drug/', {
      params: { page_size: 0 }
    });
    const allDrugs = Array.isArray(drugResponse.data) ? drugResponse.data : (drugResponse.data.results || []);
    
    // 统计每个持有人的药品数量
    const holderDrugCount = new Map();
    allDrugs.forEach((drug: any) => {
      const holderId = drug.manufacturer_holder_id || drug.manufacturer_holder;
      if (holderId) {
        holderDrugCount.set(holderId, (holderDrugCount.get(holderId) || 0) + 1);
      }
    });
    
    // 添加药品数量到持有人数据
    holderList.value = holders.map((holder: any) => ({
      ...holder,
      drug_count: holderDrugCount.get(holder.id) || 0
    }));
  } catch (error) {
    console.error('获取上市许可持有人失败:', error);
  } finally {
    loading1.value = false;
  }
};

const fetchManufacturerList = async () => {
  loading2.value = true;
  try {
    // 获取厂商列表
    const response = await api.get('/syyb/manufacturer/', {
      params: {
        page: manufacturerPage.value,
        page_size: manufacturerPageSize.value
      }
    });
    const manufacturers = response.data.results || [];
    manufacturerTotal.value = response.data.count || 0;
    
    // 获取所有药品，统计每个厂商的药品数量
    const drugResponse = await api.get('/syyb/drug/', {
      params: { page_size: 0 }
    });
    const allDrugs = Array.isArray(drugResponse.data) ? drugResponse.data : (drugResponse.data.results || []);
    
    // 统计每个厂商的药品数量
    const manufacturerDrugCount = new Map();
    allDrugs.forEach((drug: any) => {
      const manufacturerId = drug.manufacturer_id || drug.manufacturer;
      if (manufacturerId) {
        manufacturerDrugCount.set(manufacturerId, (manufacturerDrugCount.get(manufacturerId) || 0) + 1);
      }
    });
    
    // 添加药品数量到厂商数据
    manufacturerList.value = manufacturers.map((manufacturer: any) => ({
      ...manufacturer,
      drug_count: manufacturerDrugCount.get(manufacturer.id) || 0
    }));
  } catch (error) {
    console.error('获取生产厂商失败:', error);
  } finally {
    loading2.value = false;
  }
};

// 分页事件处理
const handleHolderSizeChange = (val: number) => {
  holderPageSize.value = val;
  holderPage.value = 1;
  fetchHolderList();
};

const handleHolderPageChange = (val: number) => {
  holderPage.value = val;
  fetchHolderList();
};

const handleManufacturerSizeChange = (val: number) => {
  manufacturerPageSize.value = val;
  manufacturerPage.value = 1;
  fetchManufacturerList();
};

const handleManufacturerPageChange = (val: number) => {
  manufacturerPage.value = val;
  fetchManufacturerList();
};

const handleAddHolder = () => { dialogType.value = 'holder'; isEdit.value = false; form.id = null; form.name = ''; form.abbreviation = ''; dialogVisible.value = true; };
const handleEditHolder = (row: any) => { dialogType.value = 'holder'; isEdit.value = true; form.id = row.id; form.name = row.name; form.abbreviation = row.abbreviation || ''; dialogVisible.value = true; };
const handleDeleteHolder = (row: any) => {
  ElMessageBox.confirm(`确定要删除 "${row.name}" 吗？`, '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }).then(async () => {
    try { await api.delete(`/syyb/manufacturerholder/${row.id}/`); ElMessage.success('删除成功'); fetchHolderList(); } catch (error) { console.error('删除失败:', error); }
  });
};
const handleAddManufacturer = () => { dialogType.value = 'manufacturer'; isEdit.value = false; form.id = null; form.name = ''; form.abbreviation = ''; dialogVisible.value = true; };
const handleEditManufacturer = (row: any) => { dialogType.value = 'manufacturer'; isEdit.value = true; form.id = row.id; form.name = row.name; form.abbreviation = row.abbreviation || ''; dialogVisible.value = true; };
const handleDeleteManufacturer = (row: any) => {
  ElMessageBox.confirm(`确定要删除 "${row.name}" 吗？`, '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }).then(async () => {
    try { await api.delete(`/syyb/manufacturer/${row.id}/`); ElMessage.success('删除成功'); fetchManufacturerList(); } catch (error) { console.error('删除失败:', error); }
  });
};
const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        const endpoint = dialogType.value === 'holder' ? 'manufacturerholder' : 'manufacturer';
        const payload = { name: form.name, abbreviation: form.abbreviation || undefined };
        if (isEdit.value && form.id) { await api.put(`/syyb/${endpoint}/${form.id}/`, payload); } 
        else { await api.post(`/syyb/${endpoint}/`, payload); }
        ElMessage.success(isEdit.value ? '更新成功' : '添加成功');
        dialogVisible.value = false;
        dialogType.value === 'holder' ? fetchHolderList() : fetchManufacturerList();
      } catch (error) { console.error('提交失败:', error); } 
      finally { submitting.value = false; }
    }
  });
};
onMounted(() => { fetchHolderList(); fetchManufacturerList(); });
</script>

<style scoped>
.manufacturer-page { padding: 0; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #303133; margin: 0 0 8px 0; }
.page-header p { font-size: 14px; color: #909399; margin: 0; }
.manufacturer-tabs { border-radius: 12px; overflow: hidden; }
.manufacturer-tabs :deep(.el-tabs__header) { margin: 0; background: #fff; border-bottom: 1px solid #ebeef5; }
.manufacturer-tabs :deep(.el-tabs__content) { padding: 20px; background: #fff; }
.tab-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-actions { display: flex; align-items: center; gap: 12px; }
.tab-desc { font-size: 14px; color: #909399; }
.manufacturer-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.manufacturer-card { display: flex; align-items: flex-start; gap: 12px; padding: 16px; background: #fff; border-radius: 12px; border: 2px solid transparent; transition: all 0.3s ease; position: relative; }
.manufacturer-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-2px); border-color: #409eff; }
.manufacturer-card.selected { border-color: #409eff; background: #f0f9ff; }
.card-checkbox { margin-right: 4px; padding-top: 4px; }
.manufacturer-card.add-card { border-style: dashed; background: #fafafa; cursor: pointer; align-items: center; }
.manufacturer-card.add-card:hover { background: #f0f9ff; border-color: #409eff; }
.card-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: #fff; margin-top: 2px; }
.card-icon.blue { background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%); }
.card-icon.green { background: linear-gradient(135deg, #67C23A 0%, #95d475 100%); }
.add-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.add-icon.blue { background: #e6f2ff; color: #409eff; }
.add-icon.green { background: #f0f9eb; color: #67c23a; }
.card-content { flex: 1; min-width: 0; overflow: hidden; }
.card-title { font-size: 15px; font-weight: 600; color: #303133; margin: 0 0 10px 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; max-height: 42px; }
.card-desc { font-size: 13px; color: #909399; margin: 0; }
.card-meta-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 6px; }
.card-meta-row .el-tag { font-size: 11px; height: 22px; padding: 0 8px; border-radius: 4px; line-height: 20px; }
.abbr-tag { background: #f5f7fa; border-color: #e4e7ed; color: #606266; }
.drug-count-tag { display: inline-flex; align-items: center; gap: 4px; font-weight: 500; }
.card-actions { display: flex; gap: 2px; opacity: 0; transition: opacity 0.3s ease; flex-direction: column; padding-top: 2px; }
.manufacturer-card:hover .card-actions { opacity: 1; }
.card-actions .el-button { padding: 4px 6px; }
.card-actions .action-text { font-size: 12px; margin-left: 2px; }
.pagination-wrapper {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
}

/* 药品对话框样式 */
.drugs-container {
  min-height: 300px;
}

.drugs-stats {
  margin-bottom: 20px;
}

.drugs-stats .el-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  padding: 8px 16px;
}

.drugs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.drug-item {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.drug-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.drug-image-wrapper {
  height: 120px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.drug-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.drug-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.drug-hot-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 6px;
  border-radius: 4px;
  background: #f56c6c;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
}

.drug-content {
  padding: 12px;
}

.drug-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-subname {
  font-size: 12px;
  color: #909399;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-spec {
  font-size: 12px;
  color: #606266;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drug-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

/* 药品详情样式 */
.drug-detail {
  padding: 10px 0;
}

.drug-detail .detail-header {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.drug-detail .detail-image {
  flex-shrink: 0;
}

.detail-image-placeholder {
  width: 120px;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  color: #c0c4cc;
}

.drug-detail .detail-title {
  flex: 1;
}

.drug-detail .detail-title h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.drug-detail .detail-title .subtitle {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.drug-detail .detail-tags {
  display: flex;
  gap: 8px;
}

.drug-detail .detail-section {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.drug-detail .section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #303133;
}

.drug-detail .section-content {
  color: #606266;
  line-height: 1.6;
}

.drug-detail .description-text {
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .manufacturer-grid { grid-template-columns: 1fr; }
  .tab-header { flex-direction: column; gap: 12px; align-items: flex-start; }
  .pagination-wrapper { justify-content: center; }
  .drugs-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
