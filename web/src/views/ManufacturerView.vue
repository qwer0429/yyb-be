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
              <h4 class="card-title">{{ item.name }}</h4>
              <div class="card-tags">
                <el-tag v-if="item.abbreviation" type="primary" size="small" effect="light">{{ item.abbreviation }}</el-tag>
                <el-tag type="info" size="small" effect="plain">ID: {{ item.id }}</el-tag>
              </div>
            </div>
            <div class="card-actions">
              <el-button type="primary" text size="small" @click="handleEditHolder(item)"><el-icon><Edit /></el-icon></el-button>
              <el-button type="danger" text size="small" @click="handleDeleteHolder(item)"><el-icon><Delete /></el-icon></el-button>
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
              <h4 class="card-title">{{ item.name }}</h4>
              <div class="card-tags">
                <el-tag v-if="item.abbreviation" type="success" size="small" effect="light">{{ item.abbreviation }}</el-tag>
                <el-tag type="info" size="small" effect="plain">ID: {{ item.id }}</el-tag>
              </div>
            </div>
            <div class="card-actions">
              <el-button type="primary" text size="small" @click="handleEditManufacturer(item)"><el-icon><Edit /></el-icon></el-button>
              <el-button type="danger" text size="small" @click="handleDeleteManufacturer(item)"><el-icon><Delete /></el-icon></el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import api from '../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { Plus, Edit, Delete, OfficeBuilding, OfficeBuilding as Factory } from '@element-plus/icons-vue';

const holderList = ref([]);
const manufacturerList = ref([]);
const loading1 = ref(false);
const loading2 = ref(false);
const activeTab = ref('holder');
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

const dialogTitle = computed(() => {
  const typeText = dialogType.value === 'holder' ? '上市许可持有人' : '生产厂商';
  return `${isEdit.value ? '编辑' : '新增'}${typeText}`;
});

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
.manufacturer-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.manufacturer-card { display: flex; align-items: center; gap: 16px; padding: 20px; background: #fff; border-radius: 12px; border: 2px solid transparent; transition: all 0.3s ease; position: relative; }
.manufacturer-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-2px); border-color: #409eff; }
.manufacturer-card.selected { border-color: #409eff; background: #f0f9ff; }
.card-checkbox { margin-right: 4px; }
.manufacturer-card.add-card { border-style: dashed; background: #fafafa; cursor: pointer; }
.manufacturer-card.add-card:hover { background: #f0f9ff; border-color: #409eff; }
.card-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: #fff; }
.card-icon.blue { background: linear-gradient(135deg, #409EFF 0%, #79bbff 100%); }
.card-icon.green { background: linear-gradient(135deg, #67C23A 0%, #95d475 100%); }
.add-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.add-icon.blue { background: #e6f2ff; color: #409eff; }
.add-icon.green { background: #f0f9eb; color: #67c23a; }
.card-content { flex: 1; min-width: 0; }
.card-title { font-size: 16px; font-weight: 600; color: #303133; margin: 0 0 8px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-desc { font-size: 13px; color: #909399; margin: 0; }
.card-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.card-actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.3s ease; }
.manufacturer-card:hover .card-actions { opacity: 1; }
@media (max-width: 768px) {
  .manufacturer-grid { grid-template-columns: 1fr; }
  .tab-header { flex-direction: column; gap: 12px; align-items: flex-start; }
}
</style>
