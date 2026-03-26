"""simpleserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DrugViewSet, Type1DrugViewSet, Type2DrugViewSet, ManufacturerViewSet, ManufacturerHolderViewSet,
    Type2DrugsByType1View, DrugsByType2View, FamilyUseList, SearchManufacturer, 
    SearchManufacturerHolder, SearchAnything, AllType1WithType2View, BatchDeleteDrugs,
    BatchDeleteType1Drug, BatchDeleteType2Drug, BatchDeleteManufacturer, BatchDeleteManufacturerHolder,
    add_drugs_from_excel, download_import_template, preview_import_excel, batch_import_drugs_simple,
    upload_drug_image, delete_drug_image,
    MedicineCabinetViewSet, CabinetDrugViewSet, CabinetDrugsByCabinetView,
    UpdateCabinetDrugQuantityView, ExpiringDrugsView, DefaultCabinetView,
    async_import_drugs, get_import_task_status, list_import_tasks, cancel_import_task,
    async_batch_import_simple
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
#from sblogmd import urls as sblogmd_urls
#from scloud import urls as scloud_urls

app_name = 'syyb'
urlpatterns = [
    # path('register/', UserViewSet.as_view(), name='token_register'),
    path('type1_type2/<int:type1_id>/', Type2DrugsByType1View.as_view(), name='type2-drugs-by-type1'),
    path('type2_drugs/<int:type2_id>/', DrugsByType2View.as_view(), name='drugs-by-type2'),
    path('family_use_list/', FamilyUseList.as_view(), name='family_use_list'),
    path('search_manufacturer/', SearchManufacturer.as_view(), name='search_manufacturer'),
    path('search_manufacturer_holder/',SearchManufacturerHolder.as_view(),name='search_manufacturer_holder'),
    path('search_anything/',SearchAnything.as_view(),name='search_anything'),
    path('all_type1_with_type2/', AllType1WithType2View.as_view(), name='all-type1-with-type2'),
    path('batch_delete_drugs/', BatchDeleteDrugs.as_view(), name='batch-delete-drugs'),
    path('type1drug/batch_delete/', BatchDeleteType1Drug.as_view(), name='batch-delete-type1'),
    path('type2drug/batch_delete/', BatchDeleteType2Drug.as_view(), name='batch-delete-type2'),
    path('manufacturer/batch_delete/', BatchDeleteManufacturer.as_view(), name='batch-delete-manufacturer'),
    path('manufacturerholder/batch_delete/', BatchDeleteManufacturerHolder.as_view(), name='batch-delete-holder'),
    path('add_drugs_from_excel/', add_drugs_from_excel, name='add_drugs_from_excel'),
    path('batch_import_drugs_simple/', batch_import_drugs_simple, name='batch-import-simple'),
    path('download_import_template/', download_import_template, name='download-import-template'),
    path('preview_import_excel/', preview_import_excel, name='preview-import-excel'),
    
    # 后台线程异步导入接口
    path('async_import_drugs/', async_import_drugs, name='async-import-drugs'),
    path('async_batch_import_simple/', async_batch_import_simple, name='async-batch-import-simple'),
    path('import_task_status/<str:task_id>/', get_import_task_status, name='import-task-status'),
    path('import_tasks/', list_import_tasks, name='list-import-tasks'),
    path('import_tasks/<str:task_id>/cancel/', cancel_import_task, name='cancel-import-task'),
    
    # 药品图片上传/删除
    path('drugs/<int:drug_id>/upload_image/', upload_drug_image, name='upload-drug-image'),
    path('drugs/<int:drug_id>/delete_image/', delete_drug_image, name='delete-drug-image'),
    
    # ==================== 药箱模块路由 ====================
    path('cabinets/<int:cabinet_id>/drugs/', CabinetDrugsByCabinetView.as_view(), name='cabinet-drugs'),
    path('cabinet_drugs/<int:pk>/quantity/', UpdateCabinetDrugQuantityView.as_view(), name='update-cabinet-drug-quantity'),
    path('expiring_drugs/', ExpiringDrugsView.as_view(), name='expiring-drugs'),
    path('default_cabinet/', DefaultCabinetView.as_view(), name='default-cabinet'),

]
router = DefaultRouter()
router.register(r"type1drug", viewset=Type1DrugViewSet)
router.register(r"type2drug", viewset=Type2DrugViewSet)
router.register(r"manufacturer", viewset=ManufacturerViewSet)
router.register(r"manufacturerholder", viewset=ManufacturerHolderViewSet)
router.register(r"drug", viewset=DrugViewSet)
# 药箱模块路由
router.register(r"cabinets", viewset=MedicineCabinetViewSet, basename='cabinet')
router.register(r"cabinet_drugs", viewset=CabinetDrugViewSet, basename='cabinet-drug')
# router.register(r"wordscore", viewset=WordScoreViewSet, basename='wordscore')

urlpatterns += router.urls
