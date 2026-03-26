import io
from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, date
from django.forms.models import model_to_dict

# from django.http import StreamingHttpResponse
from django.http import FileResponse
from susers.api import token_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django import db

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .pagination import CustomPagination

import uuid
import json
import pdb
import re
import requests
import os
import subprocess
import random
import logging
import threading
import time
from django.db.models import Q
from rest_framework import viewsets, filters, permissions, mixins
from .serializers import (
    DrugSerializer,
    DrugListSerializer,
    ManufacturerHolderSerializer,
    ManufacturerSerializer,
    Type1DrugSerializer,
    Type2DrugSerializer,
    Type1GetType2Serializer,
    MedicineCabinetSerializer,
    CabinetDrugListSerializer,
    CabinetDrugCreateSerializer,
    CabinetDrugUpdateSerializer,
    ExpiringDrugSerializer,
)
from .models import Drug, Manufacturer, ManufacturerHolder, Type1Drug, Type2Drug, MedicineCabinet, CabinetDrug
from .import_tasks import task_manager, run_import_in_thread

# 列名映射：中文列名 -> 英文列名
COLUMN_NAME_MAPPING = {
    '药品名(必填)': 'drug_name',
    '药品名（英文）': 'drug_name_en',
    '商品名': 'trade_name',
    '商品名（英文）': 'trade_name_en',
    '规格': 'specification',
    '剂型': 'dosage_form',
    '给药途径': 'administration_route',
    '活性成分': 'active_ingredient',
    '活性成分（英文）': 'active_ingredient_en',
    '批准文号': 'approval_number',
    '批准日期': 'approval_date',
    'ATC代码': 'atc_code',
    '医保': 'medical_insurance',
    '上市销售状况': 'market_status',
    '收录类别': 'category',
    '家庭常用清单': 'family_use',
    '京东链接': 'jd_url',
    '一级分类': 'Type1Drug_name',
    '二级分类': 'Type2Drug_name',
    '生产厂商': 'Manufacturer_name',
    '厂商简称': 'Manufacturer_abb',
    '上市许可持有人': 'ManufacturerHolder_name',
    '持有人简称': 'ManufacturerHolder_abb',
    '适用症状': 'indications',
    '药品说明': 'description',
    '图片文件名': 'drug_image_filename',
}

def get_row_value(row, field_name):
    """
    从行数据中获取值，支持中英文列名
    先尝试英文列名，如果为空则尝试中文列名
    """
    # 首先尝试英文列名
    value = row.get(field_name, '')
    if value and str(value).strip():
        return value
    
    # 查找对应的中文列名
    for cn_name, en_name in COLUMN_NAME_MAPPING.items():
        if en_name == field_name:
            value = row.get(cn_name, '')
            if value and str(value).strip():
                return value
    
    return ''

from simpleserver.settings import (
    FSAT_YYB_TOKEN,
    FSAT_YYB_URL,
)

import os
import pandas as pd
import traceback
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

logger = logging.getLogger(__name__)

# Excel 导入所需的字段配置
EXCEL_IMPORT_FIELDS = {
    'drug_name': {'required': True, 'label': '药品名', 'description': '药品通用名（必填）', 'max_length': 255},
    'drug_name_en': {'required': False, 'label': '药品名（英文）', 'description': '英文药品名', 'max_length': 255},
    'trade_name': {'required': False, 'label': '商品名', 'description': '商品名/品牌名', 'max_length': 255},
    'trade_name_en': {'required': False, 'label': '商品名（英文）', 'description': '英文商品名', 'max_length': 255},
    'specification': {'required': False, 'label': '规格', 'description': '如：0.25g*24粒', 'max_length': 255},
    'dosage_form': {'required': False, 'label': '剂型', 'description': '如：胶囊、片剂', 'max_length': 100},
    'administration_route': {'required': False, 'label': '给药途径', 'description': '如：口服、注射', 'max_length': 100},
    'active_ingredient': {'required': False, 'label': '活性成分', 'description': '主要成分', 'max_length': 255},
    'active_ingredient_en': {'required': False, 'label': '活性成分（英文）', 'description': '英文成分名', 'max_length': 1000},
    'approval_number': {'required': False, 'label': '批准文号', 'description': '国药准字', 'max_length': 100},
    'approval_date': {'required': False, 'label': '批准日期', 'description': '格式：YYYY-MM-DD'},
    'atc_code': {'required': False, 'label': 'ATC代码', 'description': 'ATC分类代码', 'max_length': 50},
    'medical_insurance': {'required': False, 'label': '医保', 'description': '甲类/乙类/非医保', 'max_length': 255},
    'market_status': {'required': False, 'label': '上市销售状况', 'description': '在售/停产/退市', 'max_length': 100},
    'category': {'required': False, 'label': '收录类别', 'description': '分类信息', 'max_length': 255},
    'family_use': {'required': False, 'label': '家庭常用清单', 'description': '常用标记', 'max_length': 100},
    'jd_url': {'required': False, 'label': '京东链接', 'description': '电商链接'},
    'Type1Drug_name': {'required': False, 'label': '一级分类', 'description': '如：西药', 'max_length': 255},
    'Type2Drug_name': {'required': False, 'label': '二级分类', 'description': '如：抗生素', 'max_length': 255},
    'Manufacturer_name': {'required': False, 'label': '生产厂商', 'description': '生产厂家全称', 'max_length': 255},
    'Manufacturer_abb': {'required': False, 'label': '厂商简称', 'description': '厂商简称', 'max_length': 100},
    'ManufacturerHolder_name': {'required': False, 'label': '上市许可持有人', 'description': '持有人全称', 'max_length': 255},
    'ManufacturerHolder_abb': {'required': False, 'label': '持有人简称', 'description': '持有人简称', 'max_length': 100},
    'indications': {'required': False, 'label': '适用症状', 'description': '如：感冒、发热、头痛'},
    'description': {'required': False, 'label': '药品说明', 'description': '用法用量、注意事项等'},
    'drug_image_filename': {'required': False, 'label': '图片文件名', 'description': '图片文件名（如：drug001.jpg），需同时上传对应图片文件', 'max_length': 255},
}


def validate_row_data(row):
    """
    校验单行数据是否符合字段长度限制
    返回: (是否通过, 错误信息列表)
    """
    errors = []
    
    for field_name, config in EXCEL_IMPORT_FIELDS.items():
        value = get_row_value(row, field_name)
        
        # 必填校验
        if config.get('required') and not value:
            errors.append(f"{config['label']} 为必填项")
            continue
        
        # 长度校验
        if value and 'max_length' in config:
            value_str = str(value)
            max_len = config['max_length']
            if len(value_str) > max_len:
                errors.append(f"{config['label']} 长度超过限制（{len(value_str)}/{max_len}字符）")
    
    return len(errors) == 0, errors


def check_drug_uniqueness(row):
    """
    校验药品唯一性（药品名 + 批准文号 + 厂商简称）
    返回: (是否唯一, 已存在的药品对象或None)
    """
    drug_name = get_row_value(row, 'drug_name')
    approval_number = get_row_value(row, 'approval_number')
    manufacturer_abb = get_row_value(row, 'Manufacturer_abb')
    
    # 如果缺少任一关键字段，跳过唯一性校验（让其他校验处理）
    if not drug_name:
        return True, None
    
    # 构建查询条件
    query = Q(drug_name=drug_name)
    
    if approval_number:
        query &= Q(approval_number=approval_number)
    
    if manufacturer_abb:
        query &= Q(manufacturer__abbreviation=manufacturer_abb)
    
    # 查询是否已存在
    existing = Drug.objects.filter(query).first()
    
    return existing is None, existing


class OneChatFast:
    def __init__(self, prompt_text):
        self.prompt_text = prompt_text

    def post(self, time_out=60):
        # pdb.set_trace()
        prompt_text = self.prompt_text
        # 设置HTTP请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + FSAT_YYB_TOKEN,
        }

        # 设置请求数据
        data = {
            "model": "qwen-max",
            "messages": prompt_text,
            "temperature": 0.3,
            "top_p": 1,
            "repetition_penalty": 1.05,
            "max_tokens": 8000,
        }

        # 发送HTTP请求
        response = requests.post(
            url=FSAT_YYB_URL,
            headers=headers,
            data=json.dumps(data),
            stream=True,
            timeout=time_out,
        )

        return response.json()


class DrugViewSet(viewsets.ModelViewSet):
    # 保留 queryset 属性供 router 自动识别 basename
    queryset = Drug.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    
    def get_serializer_class(self):
        # 列表查询使用简化版序列化器，详情查询使用完整版
        if self.action == 'list':
            return DrugListSerializer
        return DrugSerializer
    
    def get_queryset(self):
        # 使用 select_related 预加载关联对象，避免 N+1 查询问题
        return Drug.objects.select_related(
            'manufacturer',
            'manufacturer_holder',
            'type2_drug',
            'type2_drug__type1_drug'
        ).order_by("-is_hot", "-id")


class Type1DrugViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """一级分类管理视图集 - 禁用单个详情查询，只保留列表和增删改"""
    queryset = Type1Drug.objects.prefetch_related('type2drug_set').order_by('id')
    serializer_class = Type1DrugSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination


class Type2DrugViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """二级分类管理视图集 - 禁用单个详情查询，只保留列表和增删改"""
    queryset = Type2Drug.objects.all().order_by('id')
    serializer_class = Type2DrugSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        # 预加载关联的药品数据，避免 N+1 查询
        return Type2Drug.objects.prefetch_related('drug_set').order_by('id')


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination


class ManufacturerHolderViewSet(viewsets.ModelViewSet):
    queryset = ManufacturerHolder.objects.all()
    serializer_class = ManufacturerHolderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination


class Type2DrugsByType1View(APIView):
    """
    查询一级分类下的所有二级分类和药品数量
    """

    permission_classes = [permissions.AllowAny]
    queryset = Type2Drug.objects.all()
    serializer_class = Type2DrugSerializer

    def get(self, request, type1_id):

        # 获取一级分类
        type1 = Type1Drug.objects.get(id=type1_id)

        # 获取该一级分类下的所有二级分类
        type2_drugs = type1.type2drug_set.all()

        # 序列化二级分类数据
        serializer = Type2DrugSerializer(type2_drugs, many=True)

        return Response(
            {"count": len(serializer.data), "results": serializer.data},
            status=status.HTTP_200_OK,
        )


class DrugsByType2View(APIView):
    """
    查询二级分类下的所有药品信息
    """

    permission_classes = [permissions.AllowAny]  # 允许所有用户访问
    serializer_class = DrugSerializer  # 指定序列化器

    def get(self, request, type2_id):

        # 获取二级分类
        type2_drug = Type2Drug.objects.get(id=type2_id)

        # 获取该二级分类下的所有药品
        drugs = type2_drug.drug_set.all()

        # 序列化药品数据
        serializer = self.serializer_class(drugs, many=True, context={"request": request})
        return Response(
            {"count": len(serializer.data), "results": serializer.data},
            status=status.HTTP_200_OK,
        )


class FamilyUseList(APIView):
    """
    接口用于家庭常备清单数据展示
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        family_use = request.data.get("family_use", "")

        # 参数校验
        if not family_use:
            return Response(
                {"error": "缺少family_use参数"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 查询数据库
        drugs = Drug.objects.filter(family_use=family_use)
        results = DrugSerializer(drugs, many=True, context={"request": request})

        return Response(
            {"count": len(results.data), "results": results.data},
            status=status.HTTP_200_OK,
        )


class SearchManufacturer(APIView):
    """
    接口用于根据生产厂商查询药品信息
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        manufacturer = request.data.get("manufacturer", "")

        # 参数校验
        if not manufacturer:
            return Response(
                {"error": "缺少manufacturer参数"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 查询数据库（通过生产厂商全称查询）
        drugs = Drug.objects.filter(manufacturer__name=manufacturer)
        results = DrugSerializer(drugs, many=True, context={"request": request})

        return Response(
            {"count": len(results.data), "results": results.data},
            status=status.HTTP_200_OK,
        )


class SearchManufacturerHolder(APIView):
    """
    接口用于根据上市许可持有人查询药品信息
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        manufacturer_holder = request.data.get("manufacturer_holder", "")

        # 参数校验
        if not manufacturer_holder:
            return Response(
                {"error": "缺少manufacturer_holder参数"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 查询数据库（通过上市许可持有人全称查询）
        drugs = Drug.objects.filter(manufacturer_holder__name=manufacturer_holder)
        results = DrugSerializer(drugs, many=True, context={"request": request})

        return Response(
            {"count": len(results.data), "results": results.data},
            status=status.HTTP_200_OK,
        )


# class SearchAnything(APIView):
#     """
#     接口用于搜索栏
#     """
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         text = request.data.get('text', "")


#         if not text:
#             return Response(
#                 {"error": "缺少text参数"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )


#         drugs = Drug.objects.filter(
#             Q(drug_name=text) |
#             Q(trade_name=text)|
#             Q(manufacturer=text)
#         )

#         results = DrugSerializer(drugs, many=True,context={'request':request})

#         return Response({
#             "count": drugs.count(),
#             "results": results.data
#         }, status=status.HTTP_200_OK)


class SearchAnything(APIView):
    """
    支持药品名、商品名、厂商信息的模糊搜索
    (匹配字段包含：药品名、英文药品名、商品名、英文商品名、厂商全称、厂商简称)
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        search_text = request.data.get("text", "").strip()

        if not search_text:
            return Response(
                {"error": "请输入搜索内容"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 构建多字段模糊查询条件
        query = Q()
        query |= Q(drug_name__icontains=search_text)
        query |= Q(drug_name_en__icontains=search_text)
        query |= Q(trade_name__icontains=search_text)
        query |= Q(trade_name_en__icontains=search_text)
        query |= Q(manufacturer__name__icontains=search_text)
        query |= Q(manufacturer__abbreviation__icontains=search_text)

        # 执行查询并优化
        drugs = (
            Drug.objects.filter(query)
            .distinct()
            .select_related("manufacturer")
            .order_by("-approval_date")
        )  # 按批准日期倒序

        # 序列化结果
        serializer = DrugSerializer(drugs, many=True, context={"request": request})

        return Response(
            {"count": drugs.count(), "results": serializer.data},
            status=status.HTTP_200_OK,
        )


class AllType1WithType2View(APIView):
    """
    查询所有一级分类及其对应的二级分类的id和name
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # 获取所有一级分类
        type1_drugs = Type1Drug.objects.all()
        result = []

        for type1 in type1_drugs:
            # 获取该一级分类下的所有二级分类
            type2_drugs = type1.type2drug_set.all()

            # 序列化二级分类数据
            type2_serializer = Type2DrugSerializer(type2_drugs, many=True)

            # 过滤掉序列化结果中的非必要字段，并替换字段名
            filtered_type2_data = [
                {"value": item["id"], "label": item["name"]}
                for item in type2_serializer.data
            ]

            # 构建结果
            result.append(
                {
                    "value": type1.id,
                    "label": type1.name,
                    "children": filtered_type2_data,
                }
            )

        return Response(
            {"count": len(result), "results": result},
            status=status.HTTP_200_OK,
        )


class BatchDeleteDrugs(APIView):
    """
    接口用于批量删除药品数据
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        drug_ids = request.data.get("drug_ids", [])

        # 参数校验
        if not drug_ids:
            return Response(
                {"error": "缺少drug_ids参数"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 查询数据库并删除
        deleted_count, _ = Drug.objects.filter(id__in=drug_ids).delete()

        return Response(
            {"count": deleted_count, "message": f"成功删除{deleted_count}条药品数据"},
            status=status.HTTP_200_OK,
        )


def add_drugs_from_excel(request):
    """
    上传 Excel 文件，批量添加药品记录（不导入图片）
    
    图片请使用单独的上传功能：上传图片到药品

    优化方案：预创建分类数据，避免事务内的 get_or_create 竞争锁
    """
    if request.FILES.get("file"):
        file = request.FILES["file"]
        # 判断文件是否是 Excel 文件
        if not file.name.lower().endswith(
            (".xls", ".xlsx", ".xlsm", ".xlsb", ".odf", ".ods")
        ):
            return JsonResponse(
                {"error": "文件类型错误，只允许上传 Excel 文件"}, status=400
            )

        try:
            # 注意：不再处理图片文件，只导入药品数据
            data = file.read()
            excel_file = pd.ExcelFile(io.BytesIO(data))
            
            # ========== 第一遍：收集所有需要预创建的数据 ==========
            type1_names = set()
            type2_mapping = {}  # {type1_name: set(type2_names)}
            holder_names = {}   # {name: abbreviation}
            manufacturer_names = {}  # {name: abbreviation}
            all_rows = []  # 存储所有有效行数据供第二遍使用

            for sheet_name in excel_file.sheet_names:
                # 跳过说明sheet
                if sheet_name == "填写说明":
                    continue
                    
                df = excel_file.parse(sheet_name).fillna("")

                for i in range(1, len(df)):
                    row = df.iloc[i]
                    # 检查药品名称是否为空
                    drug_name = get_row_value(row, 'drug_name')
                    if not drug_name or not isinstance(drug_name, str):
                        continue  # 跳过空行

                    # 收集分类数据
                    type1_name = get_row_value(row, 'Type1Drug_name')
                    type2_name = get_row_value(row, 'Type2Drug_name')
                    if type1_name:
                        type1_names.add(type1_name)
                        if type2_name:
                            type2_mapping.setdefault(type1_name, set()).add(type2_name)

                    # 收集持有人数据
                    holder_name = get_row_value(row, 'ManufacturerHolder_name')
                    if holder_name:
                        holder_names[holder_name] = get_row_value(row, 'ManufacturerHolder_abb')

                    # 收集生产商数据
                    manufacturer_name = get_row_value(row, 'Manufacturer_name')
                    if manufacturer_name:
                        manufacturer_names[manufacturer_name] = get_row_value(row, 'Manufacturer_abb')

                    # 保存行数据供后续使用
                    all_rows.append({
                        'row': row,
                        'sheet_name': sheet_name,
                        'row_index': i,
                    })

            # ========== 第二遍：批量预创建所有分类和关联数据 ==========
            
            # 1. 批量创建一级分类
            with transaction.atomic():
                if type1_names:
                    Type1Drug.objects.bulk_create(
                        [Type1Drug(name=name) for name in type1_names],
                        ignore_conflicts=True
                    )
            
            # 查询所有一级分类（包括已存在的和新创建的）
            type1_objs = {t.name: t for t in Type1Drug.objects.filter(name__in=type1_names)}

            # 2. 批量创建二级分类
            with transaction.atomic():
                type2_to_create = []
                for t1_name, t2_names in type2_mapping.items():
                    t1 = type1_objs.get(t1_name)
                    if t1:
                        for t2_name in t2_names:
                            type2_to_create.append(Type2Drug(name=t2_name, type1_drug=t1))
                
                if type2_to_create:
                    Type2Drug.objects.bulk_create(type2_to_create, ignore_conflicts=True)
            
            # 查询所有二级分类
            type2_qs = Type2Drug.objects.filter(
                type1_drug__name__in=type1_names
            ).select_related('type1_drug')
            type2_objs = {}
            for t2 in type2_qs:
                key = (t2.type1_drug.name, t2.name)
                type2_objs[key] = t2

            # 3. 批量创建上市许可持有人
            with transaction.atomic():
                if holder_names:
                    ManufacturerHolder.objects.bulk_create(
                        [
                            ManufacturerHolder(name=name, abbreviation=abb)
                            for name, abb in holder_names.items()
                        ],
                        ignore_conflicts=True
                    )
            
            holder_objs = {h.name: h for h in ManufacturerHolder.objects.filter(name__in=holder_names.keys())}

            # 4. 批量创建生产商
            with transaction.atomic():
                if manufacturer_names:
                    Manufacturer.objects.bulk_create(
                        [
                            Manufacturer(name=name, abbreviation=abb)
                            for name, abb in manufacturer_names.items()
                        ],
                        ignore_conflicts=True
                    )
            
            manufacturer_objs = {m.name: m for m in Manufacturer.objects.filter(name__in=manufacturer_names.keys())}

            # ========== 第三遍：逐个处理药品（每个药品独立事务） ==========
            created_drugs = []
            error_list = []
            skipped_duplicates = []  # 记录因重复被跳过的药品

            for row_data in all_rows:
                row = row_data['row']

                # 数据校验
                is_valid, validation_errors = validate_row_data(row)
                if not is_valid:
                    error_list.append({
                        'drug_name': get_row_value(row, 'drug_name') or f'第{row_data["row_index"]+1}行',
                        'error': '; '.join(validation_errors)
                    })
                    continue

                # 唯一性校验（药品名 + 批准文号 + 厂商简称）
                is_unique, existing_drug = check_drug_uniqueness(row)
                if not is_unique:
                    manufacturer_name = get_row_value(row, 'Manufacturer_name')
                    skipped_duplicates.append({
                        'drug_name': get_row_value(row, 'drug_name'),
                        'manufacturer': manufacturer_name or get_row_value(row, 'Manufacturer_abb') or '未知厂商',
                        'approval_number': get_row_value(row, 'approval_number') or '',
                        'reason': '数据库中已存在相同药品名+批准文号+厂商的药品'
                    })
                    continue

                # 构建药品字典（不包含图片）
                drug_data = {
                    "drug_name": get_row_value(row, 'drug_name'),
                    "drug_name_en": get_row_value(row, 'drug_name_en'),
                    "trade_name": get_row_value(row, 'trade_name'),
                    "trade_name_en": get_row_value(row, 'trade_name_en'),
                    "medical_insurance": get_row_value(row, 'medical_insurance'),
                    "jd_url": get_row_value(row, 'jd_url'),
                    "category": get_row_value(row, 'category'),
                    "specification": get_row_value(row, 'specification'),
                    "dosage_form": get_row_value(row, 'dosage_form'),
                    "administration_route": get_row_value(row, 'administration_route'),
                    "active_ingredient": get_row_value(row, 'active_ingredient'),
                    "active_ingredient_en": get_row_value(row, 'active_ingredient_en'),
                    "approval_number": get_row_value(row, 'approval_number'),
                    "approval_date": get_row_value(row, 'approval_date'),
                    "atc_code": get_row_value(row, 'atc_code'),
                    "market_status": get_row_value(row, 'market_status'),
                    "family_use": get_row_value(row, 'family_use'),
                    "indications": get_row_value(row, 'indications'),
                    "description": get_row_value(row, 'description'),
                }

                try:
                    with transaction.atomic():
                        # 关联二级分类
                        type1_name = get_row_value(row, 'Type1Drug_name')
                        type2_name = get_row_value(row, 'Type2Drug_name')
                        if type1_name and type2_name:
                            type2_obj = type2_objs.get((type1_name, type2_name))
                            if type2_obj:
                                drug_data["type2_drug"] = type2_obj

                        # 关联持有人
                        holder_name = get_row_value(row, 'ManufacturerHolder_name')
                        if holder_name:
                            holder_obj = holder_objs.get(holder_name)
                            if holder_obj:
                                drug_data["manufacturer_holder"] = holder_obj

                        # 关联生产商
                        manufacturer_name = get_row_value(row, 'Manufacturer_name')
                        if manufacturer_name:
                            manufacturer_obj = manufacturer_objs.get(manufacturer_name)
                            if manufacturer_obj:
                                drug_data["manufacturer"] = manufacturer_obj

                        # 创建或更新药品（不包含图片）
                        drug, created = Drug.objects.update_or_create(
                            atc_code=drug_data["atc_code"],
                            defaults=drug_data,
                        )

                        created_drugs.append(drug.id)

                except Exception as e:
                    error_msg = f"处理药品 '{drug_data.get('drug_name')}' 失败: {str(e)}"
                    logger.error(error_msg)
                    logger.error(traceback.format_exc())
                    error_list.append({
                        'drug_name': drug_data.get('drug_name'),
                        'error': str(e)
                    })

            # 构建返回消息
            message = f"成功导入 {len(created_drugs)} 条药品记录"
            if skipped_duplicates:
                message += f"，跳过 {len(skipped_duplicates)} 条重复药品"
            if error_list:
                message += f"，{len(error_list)} 条记录处理失败"

            return JsonResponse(
                {
                    "success": True,
                    "created_count": len(created_drugs),
                    "skipped_count": len(skipped_duplicates),
                    "skipped_duplicates": skipped_duplicates[:20] if skipped_duplicates else [],  # 最多返回20条
                    "total_rows": len(all_rows),
                    "error_count": len(error_list),
                    "error_list": error_list[:10] if error_list else [],  # 只返回前10个错误
                    "message": message,
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "error": f"处理过程中发生错误: {str(e)}",
                    "traceback": traceback.format_exc(),
                },
                status=500,
            )

    else:
        return JsonResponse({"error": "未上传文件"}, status=400)


def download_import_template(request):
    """
    下载药品导入模板
    """
    # 创建工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "药品导入模板"
    
    # 设置列标题
    headers = []
    for field, config in EXCEL_IMPORT_FIELDS.items():
        header = f"{config['label']}{'(必填)' if config['required'] else ''}"
        headers.append(header)
    
    ws.append(headers)
    
    # 设置标题行样式
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # 添加示例数据行
    example_data = [
        "阿莫西林胶囊", "Amoxicillin Capsules", "阿莫仙", "Amoxicillin",
        "0.25g*24粒", "胶囊剂", "口服", "阿莫西林", "Amoxicillin",
        "国药准字H11020362", "2020-01-15", "J01CA04", "甲类", "在售",
        "抗生素类", "常用", "https://www.jd.com",
        "西药", "抗生素", "华北制药", "华北制药", "华北制药集团", "华北制药",
        "适用于敏感菌所致的呼吸道感染、泌尿生殖道感染等",
        "口服。成人一次0.5g，每6-8小时1次。注意事项：青霉素过敏者禁用。",
        "amoxicillin.jpg"
    ]
    ws.append(example_data)
    
    # 设置列宽
    for idx, (field, config) in enumerate(EXCEL_IMPORT_FIELDS.items(), 1):
        ws.column_dimensions[chr(64 + idx) if idx <= 26 else 'A' + chr(64 + idx - 26)].width = max(15, len(config['label']) + 5)
    
    # 创建说明工作表
    ws_info = wb.create_sheet("填写说明")
    ws_info.append(["字段名", "说明", "是否必填", "示例值"])
    
    # 说明表头样式
    for cell in ws_info[1]:
        cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # 添加字段说明
    for field, config in EXCEL_IMPORT_FIELDS.items():
        ws_info.append([
            config['label'],
            config['description'],
            "是" if config['required'] else "否",
            ""
        ])
    
    ws_info.column_dimensions['A'].width = 20
    ws_info.column_dimensions['B'].width = 40
    ws_info.column_dimensions['C'].width = 12
    ws_info.column_dimensions['D'].width = 30
    
    # 添加导入注意事项
    ws_info.append([])
    ws_info.append(["注意事项："])
    ws_info.append(["1. 请勿修改第一行的列标题"])
    ws_info.append(["2. 日期格式请使用 YYYY-MM-DD 格式，如：2024-01-15"])
    ws_info.append(["3. 如果一级分类和二级分类不存在，系统会自动创建"])
    ws_info.append(["4. 如果生产厂商和上市许可持有人不存在，系统会自动创建"])
    ws_info.append(["5. ATC代码是唯一标识，如果重复会更新已有记录"])
    ws_info.append(["6. 请不要删除示例行，可以在其下方继续添加数据"])
    ws_info.append(["7. 图片上传说明："])
    ws_info.append(["   - 在'图片文件名'列填写图片文件名（如：drug001.jpg）"])
    ws_info.append(["   - 导入时需同时选择对应的图片文件"])
    ws_info.append(["   - 支持格式：jpg、jpeg、png、gif、bmp、webp"])
    ws_info.append(["   - 建议图片大小不超过 5MB"])
    
    # 保存到内存
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    # 创建响应
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=药品导入模板.xlsx"
    return response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def preview_import_excel(request):
    """
    预览导入数据（不保存到数据库）
    """
    if 'file' not in request.FILES:
        return Response({"error": "未上传文件"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # 检查文件类型
    if not file.name.lower().endswith(('.xls', '.xlsx', '.xlsm', '.xlsb', '.odf', '.ods')):
        return Response({"error": "文件类型错误，只允许上传 Excel 文件"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = file.read()
        excel_file = pd.ExcelFile(io.BytesIO(data))
        
        preview_data = []
        errors = []
        total_rows = 0
        
        for sheet_name in excel_file.sheet_names:
            # 跳过说明sheet
            if sheet_name == "填写说明":
                continue
                
            df = excel_file.parse(sheet_name).fillna("")
            
            # 跳过标题行，从第二行开始
            for i in range(1, min(len(df), 11)):  # 最多预览10条
                row = df.iloc[i]
                total_rows += 1
                
                # 获取图片文件名
                image_filename = get_row_value(row, 'drug_image_filename')
                
                row_data = {
                    'row_number': i + 1,
                    'sheet_name': sheet_name,
                    'drug_name': get_row_value(row, 'drug_name'),
                    'trade_name': get_row_value(row, 'trade_name'),
                    'specification': get_row_value(row, 'specification'),
                    'dosage_form': get_row_value(row, 'dosage_form'),
                    'manufacturer_name': get_row_value(row, 'Manufacturer_name'),
                    'type1_name': get_row_value(row, 'Type1Drug_name'),
                    'type2_name': get_row_value(row, 'Type2Drug_name'),
                    'image_filename': image_filename,
                    'valid': True,
                    'errors': []
                }
                
                # 验证必填字段
                if not row_data['drug_name']:
                    row_data['valid'] = False
                    row_data['errors'].append('药品名称为空')
                
                # 字段长度校验
                _, validation_errors = validate_row_data(row)
                if validation_errors:
                    row_data['valid'] = False
                    row_data['errors'].extend(validation_errors)
                
                # 检查药品是否已存在
                if row_data['drug_name']:
                    existing = Drug.objects.filter(drug_name=row_data['drug_name']).first()
                    if existing:
                        row_data['exists'] = True
                        row_data['existing_id'] = existing.id
                
                preview_data.append(row_data)
        
        return Response({
            "success": True,
            "preview_data": preview_data,
            "total_rows": total_rows,
            "errors": errors,
            "message": f"共发现 {total_rows} 条数据，预览前 {len(preview_data)} 条"
        })
        
    except Exception as e:
        logger.error(f"预览导入失败: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({
            "error": f"预览失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== 智慧药箱模块 API ====================

class MedicineCabinetViewSet(viewsets.ModelViewSet):
    """
    药箱管理视图集
    提供药箱的增删改查功能
    """
    queryset = MedicineCabinet.objects.all()
    serializer_class = MedicineCabinetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """只返回当前用户的药箱，预加载药品数据"""
        return MedicineCabinet.objects.filter(user=self.request.user).prefetch_related('drugs')

    def perform_create(self, serializer):
        """创建药箱时自动关联当前用户"""
        # 如果是第一个药箱，设为默认
        is_default = not MedicineCabinet.objects.filter(user=self.request.user).exists()
        serializer.save(user=self.request.user, is_default=is_default)

    def perform_update(self, serializer):
        """更新药箱，处理默认药箱逻辑"""
        instance = self.get_object()
        # 如果要设为默认，先取消其他默认药箱
        if self.request.data.get('is_default') and not instance.is_default:
            MedicineCabinet.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        serializer.save()


class CabinetDrugViewSet(viewsets.ModelViewSet):
    """
    药箱药品管理视图集
    提供药箱药品的增删改查功能
    """
    queryset = CabinetDrug.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """只返回当前用户药箱中的药品，预加载关联数据"""
        return CabinetDrug.objects.filter(
            cabinet__user=self.request.user
        ).select_related(
            'drug',
            'drug__manufacturer'
        )

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return CabinetDrugCreateSerializer
        return CabinetDrugListSerializer

    def get_serializer_context(self):
        """添加请求上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        """添加药品到药箱"""
        # 验证药箱是否属于当前用户
        cabinet_id = request.data.get('cabinet')
        try:
            cabinet = MedicineCabinet.objects.get(id=cabinet_id, user=request.user)
        except MedicineCabinet.DoesNotExist:
            return Response(
                {"error": "药箱不存在或无权限访问"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # 返回完整的药品信息
        result_serializer = CabinetDrugListSerializer(serializer.instance, context={'request': request})
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        """更新药箱药品信息"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 验证药箱是否属于当前用户
        if instance.cabinet.user != request.user:
            return Response(
                {"error": "无权限修改此药品"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CabinetDrugUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # 返回完整的药品信息
        result_serializer = CabinetDrugListSerializer(instance, context={'request': request})
        return Response(result_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """从药箱中删除药品"""
        instance = self.get_object()
        
        # 验证药箱是否属于当前用户
        if instance.cabinet.user != request.user:
            return Response(
                {"error": "无权限删除此药品"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CabinetDrugsByCabinetView(APIView):
    """
    获取指定药箱中的所有药品
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, cabinet_id):
        try:
            cabinet = MedicineCabinet.objects.get(id=cabinet_id, user=request.user)
        except MedicineCabinet.DoesNotExist:
            return Response(
                {"error": "药箱不存在或无权限访问"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        drugs = CabinetDrug.objects.filter(cabinet=cabinet).select_related('drug', 'drug__manufacturer')
        
        # 可选：按过期状态筛选
        filter_type = request.query_params.get('filter', 'all')
        today = date.today()
        
        if filter_type == 'expired':
            drugs = drugs.filter(valid_until__lt=today)
        elif filter_type == 'expiring_soon':
            from datetime import timedelta
            drugs = drugs.filter(
                valid_until__gte=today,
                valid_until__lte=today + timedelta(days=7)
            )
        elif filter_type == 'valid':
            drugs = drugs.filter(valid_until__gte=today)
        
        # 排序
        sort_by = request.query_params.get('sort', '-added_at')
        drugs = drugs.order_by(sort_by)
        
        serializer = CabinetDrugListSerializer(drugs, many=True, context={'request': request})
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        }, status=status.HTTP_200_OK)


class UpdateCabinetDrugQuantityView(APIView):
    """
    更新药箱药品数量（增加或减少）
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            cabinet_drug = CabinetDrug.objects.get(
                pk=pk,
                cabinet__user=request.user
            )
        except CabinetDrug.DoesNotExist:
            return Response(
                {"error": "药品不存在或无权限访问"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        action = request.data.get('action')
        amount = request.data.get('amount', 1)
        
        if action == 'increase':
            cabinet_drug.quantity += amount
        elif action == 'decrease':
            if cabinet_drug.quantity <= amount:
                # 数量减到0，删除该药品
                cabinet_drug.delete()
                return Response(
                    {"message": "药品已从药箱中移除"},
                    status=status.HTTP_200_OK
                )
            cabinet_drug.quantity -= amount
        else:
            return Response(
                {"error": "无效的操作类型，请使用 'increase' 或 'decrease'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cabinet_drug.save()
        serializer = CabinetDrugListSerializer(cabinet_drug, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExpiringDrugsView(APIView):
    """
    获取即将过期和已过期的药品统计
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        from datetime import timedelta
        
        # 获取所有即将过期和已过期的药品
        all_drugs = CabinetDrug.objects.filter(
            cabinet__user=request.user,
            valid_until__isnull=False
        )
        
        expired_drugs = all_drugs.filter(valid_until__lt=today)
        expiring_soon_drugs = all_drugs.filter(
            valid_until__gte=today,
            valid_until__lte=today + timedelta(days=7)
        )
        valid_drugs = all_drugs.filter(valid_until__gt=today + timedelta(days=7))
        
        expired_serializer = CabinetDrugListSerializer(expired_drugs, many=True, context={'request': request})
        expiring_soon_serializer = CabinetDrugListSerializer(expiring_soon_drugs, many=True, context={'request': request})
        
        return Response({
            "expired_count": expired_drugs.count(),
            "expiring_soon_count": expiring_soon_drugs.count(),
            "valid_count": valid_drugs.count(),
            "total_count": all_drugs.count(),
            "expired_drugs": expired_serializer.data,
            "expiring_soon_drugs": expiring_soon_serializer.data,
        }, status=status.HTTP_200_OK)


class DefaultCabinetView(APIView):
    """
    获取用户的默认药箱，如果不存在则创建一个
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 获取或创建默认药箱
        cabinet, created = MedicineCabinet.objects.get_or_create(
            user=request.user,
            is_default=True,
            defaults={
                'name': '默认药箱',
                'cabinet_type': 'home',
                'description': '系统自动创建的默认药箱'
            }
        )
        
        serializer = MedicineCabinetSerializer(cabinet)
        return Response({
            "cabinet": serializer.data,
            "created": created
        }, status=status.HTTP_200_OK)


# ==================== 批量删除视图 ====================

class BatchDeleteType1Drug(APIView):
    """
    批量删除一级分类
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "缺少ids参数"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否有子分类
        type1_with_children = Type1Drug.objects.filter(
            id__in=ids, type2drug__isnull=False
        ).distinct()
        
        if type1_with_children.exists():
            names = [t.name for t in type1_with_children]
            return Response(
                {"error": f"以下分类下还有子分类，无法删除：{', '.join(names)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = Type1Drug.objects.filter(id__in=ids).delete()
        return Response(
            {"count": deleted_count, "message": f"成功删除{deleted_count}个一级分类"},
            status=status.HTTP_200_OK
        )


class BatchDeleteType2Drug(APIView):
    """
    批量删除二级分类
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "缺少ids参数"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否有药品使用这些分类
        type2_with_drugs = Type2Drug.objects.filter(
            id__in=ids, drug__isnull=False
        ).distinct()
        
        if type2_with_drugs.exists():
            names = [t.name for t in type2_with_drugs]
            return Response(
                {"error": f"以下分类下还有药品，无法删除：{', '.join(names)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = Type2Drug.objects.filter(id__in=ids).delete()
        return Response(
            {"count": deleted_count, "message": f"成功删除{deleted_count}个二级分类"},
            status=status.HTTP_200_OK
        )


class BatchDeleteManufacturer(APIView):
    """
    批量删除生产厂商
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "缺少ids参数"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否有药品使用这些厂商
        m_with_drugs = Manufacturer.objects.filter(
            id__in=ids, drug__isnull=False
        ).distinct()
        
        if m_with_drugs.exists():
            names = [m.name for m in m_with_drugs]
            return Response(
                {"error": f"以下厂商还有关联药品，无法删除：{', '.join(names)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = Manufacturer.objects.filter(id__in=ids).delete()
        return Response(
            {"count": deleted_count, "message": f"成功删除{deleted_count}个生产厂商"},
            status=status.HTTP_200_OK
        )


class BatchDeleteManufacturerHolder(APIView):
    """
    批量删除上市许可持有人
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "缺少ids参数"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查是否有药品使用这些持有人
        h_with_drugs = ManufacturerHolder.objects.filter(
            id__in=ids, drug__isnull=False
        ).distinct()
        
        if h_with_drugs.exists():
            names = [h.name for h in h_with_drugs]
            return Response(
                {"error": f"以下持有人还有关联药品，无法删除：{', '.join(names)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = ManufacturerHolder.objects.filter(id__in=ids).delete()
        return Response(
            {"count": deleted_count, "message": f"成功删除{deleted_count}个上市许可持有人"},
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def batch_import_drugs_simple(request):
    """
    轻量级批量导入药品（不处理图片，速度更快）
    用于大批量数据导入，避免超时
    """
    if not request.FILES.get("file"):
        return Response({"error": "未上传文件"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES["file"]
    if not file.name.lower().endswith((".xls", ".xlsx")):
        return Response({"error": "只支持Excel文件"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        import pandas as pd
        from django.db import transaction
        
        # 读取Excel
        df = pd.read_excel(file).fillna("")
        
        # 限制批次大小
        MAX_BATCH = 100
        if len(df) > MAX_BATCH:
            df = df.head(MAX_BATCH)
        
        created_count = 0
        skipped_count = 0
        error_list = []
        
        # 预加载所有分类和厂商
        type1_cache = {t.name: t for t in Type1Drug.objects.all()}
        type2_cache = {}
        for t2 in Type2Drug.objects.select_related('type1_drug').all():
            type2_cache[(t2.type1_drug.name, t2.name)] = t2
        
        holder_cache = {h.name: h for h in ManufacturerHolder.objects.all()}
        manufacturer_cache = {m.name: m for m in Manufacturer.objects.all()}
        
        for idx, row in df.iterrows():
            try:
                drug_name = get_row_value(row, 'drug_name')
                if not drug_name:
                    continue
                
                # 构建药品数据
                drug_data = {
                    "drug_name": drug_name,
                    "drug_name_en": get_row_value(row, 'drug_name_en'),
                    "trade_name": get_row_value(row, 'trade_name'),
                    "trade_name_en": get_row_value(row, 'trade_name_en'),
                    "medical_insurance": get_row_value(row, 'medical_insurance'),
                    "jd_url": get_row_value(row, 'jd_url'),
                    "category": get_row_value(row, 'category'),
                    "specification": get_row_value(row, 'specification'),
                    "dosage_form": get_row_value(row, 'dosage_form'),
                    "administration_route": get_row_value(row, 'administration_route'),
                    "active_ingredient": get_row_value(row, 'active_ingredient'),
                    "active_ingredient_en": get_row_value(row, 'active_ingredient_en'),
                    "approval_number": get_row_value(row, 'approval_number'),
                    "approval_date": get_row_value(row, 'approval_date') or None,
                    "atc_code": get_row_value(row, 'atc_code'),
                    "market_status": get_row_value(row, 'market_status'),
                    "family_use": get_row_value(row, 'family_use'),
                    "indications": get_row_value(row, 'indications'),
                    "description": get_row_value(row, 'description'),
                }
                
                # 关联分类
                type1_name = get_row_value(row, 'Type1Drug_name')
                type2_name = get_row_value(row, 'Type2Drug_name')
                if type1_name and type2_name:
                    type2_obj = type2_cache.get((type1_name, type2_name))
                    if type2_obj:
                        drug_data["type2_drug"] = type2_obj
                
                # 关联持有人
                holder_name = get_row_value(row, 'ManufacturerHolder_name')
                if holder_name:
                    holder_obj = holder_cache.get(holder_name)
                    if holder_obj:
                        drug_data["manufacturer_holder"] = holder_obj
                
                # 关联生产商
                manufacturer_name = get_row_value(row, 'Manufacturer_name')
                if manufacturer_name:
                    manufacturer_obj = manufacturer_cache.get(manufacturer_name)
                    if manufacturer_obj:
                        drug_data["manufacturer"] = manufacturer_obj
                
                # 检查唯一性
                is_unique, existing = check_drug_uniqueness(row)
                if not is_unique:
                    skipped_count += 1
                    continue
                
                # 创建或更新
                with transaction.atomic():
                    Drug.objects.update_or_create(
                        atc_code=drug_data.get("atc_code") or f"TEMP_{idx}",
                        defaults=drug_data
                    )
                    created_count += 1
                    
            except Exception as e:
                error_list.append({
                    'row': idx + 1,
                    'drug_name': drug_name if 'drug_name' in locals() else 'Unknown',
                    'error': str(e)
                })
        
        return Response({
            "success": True,
            "created_count": created_count,
            "skipped_count": skipped_count,
            "error_count": len(error_list),
            "errors": error_list[:5],
            "message": f"成功导入 {created_count} 条，跳过 {skipped_count} 条，失败 {len(error_list)} 条"
        })
        
    except Exception as e:
        return Response({
            "error": f"处理失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def upload_drug_image(request, drug_id):
    """
    为指定药品上传图片
    
    POST /api/drugs/<drug_id>/upload_image/
    
    请求参数:
        - image: 图片文件 (jpg, png, gif等)
    """
    try:
        drug = Drug.objects.get(id=drug_id)
    except Drug.DoesNotExist:
        return Response(
            {"error": "药品不存在"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if 'image' not in request.FILES:
        return Response(
            {"error": "请上传图片文件"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    # 检查文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
    if image_file.content_type not in allowed_types:
        return Response(
            {"error": f"不支持的文件类型: {image_file.content_type}，请上传图片文件"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 检查文件大小（最大10MB）
    max_size = 10 * 1024 * 1024  # 10MB
    if image_file.size > max_size:
        return Response(
            {"error": f"文件过大: {image_file.size / 1024 / 1024:.2f}MB，最大允许10MB"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 保存图片
        from django.core.files.base import ContentFile
        import os
        
        # 生成文件名: drug_id_原始文件名
        ext = os.path.splitext(image_file.name)[1].lower()
        new_filename = f"{drug.id}_{drug.drug_name}{ext}"
        
        # 保存到drug_image字段
        drug.drug_image.save(
            new_filename,
            ContentFile(image_file.read()),
            save=True
        )
        
        # 返回完整URL
        request = request
        image_url = request.build_absolute_uri(drug.drug_image.url) if request else drug.drug_image.url
        
        return Response({
            "success": True,
            "message": "图片上传成功",
            "drug_id": drug.id,
            "drug_name": drug.drug_name,
            "image_url": image_url,
            "filename": new_filename
        })
        
    except Exception as e:
        logger.error(f"图片上传失败: {str(e)}")
        return Response(
            {"error": f"图片上传失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.AllowAny])
def delete_drug_image(request, drug_id):
    """
    删除药品图片
    
    DELETE /api/drugs/<drug_id>/delete_image/
    """
    try:
        drug = Drug.objects.get(id=drug_id)
    except Drug.DoesNotExist:
        return Response(
            {"error": "药品不存在"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not drug.drug_image:
        return Response(
            {"error": "该药品没有图片"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 删除图片文件
        drug.drug_image.delete()
        drug.drug_image = None
        drug.save()
        
        return Response({
            "success": True,
            "message": "图片删除成功",
            "drug_id": drug.id,
            "drug_name": drug.drug_name
        })
        
    except Exception as e:
        logger.error(f"图片删除失败: {str(e)}")
        return Response(
            {"error": f"图片删除失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== 后台线程导入接口 ====================

def _process_import_task(task_id: str, excel_file, file_name: str, skip_duplicates: bool = True):
    """
    后台线程执行的导入任务处理函数
    
    Args:
        task_id: 任务ID
        excel_file: pandas ExcelFile 对象
        file_name: 原始文件名
        skip_duplicates: 是否跳过重复项
    
    Returns:
        dict: 导入结果
    """
    logger.info(f"=== 开始导入任务 {task_id} ===")
    try:
        task_manager.update_progress(task_id, 5, "正在分析Excel文件...")
        
        # ========== 第一遍：收集所有需要预创建的数据 ==========
        logger.info("开始第一遍扫描：收集数据...")
        type1_names = set()
        type2_mapping = {}  # {type1_name: set(type2_names)}
        holder_names = {}   # {name: abbreviation}
        manufacturer_names = {}  # {name: abbreviation}
        all_rows = []  # 存储所有有效行数据供第二遍使用
        total_rows = 0

        for sheet_name in excel_file.sheet_names:
            # 跳过说明sheet
            if sheet_name == "填写说明":
                continue
                
            df = excel_file.parse(sheet_name).fillna("")
            total_rows += len(df) - 1  # 减去标题行
            
            for i in range(1, len(df)):
                row = df.iloc[i]
                # 检查药品名称是否为空
                drug_name = get_row_value(row, 'drug_name')
                if not drug_name or not isinstance(drug_name, str):
                    continue  # 跳过空行

                # 收集分类数据
                type1_name = get_row_value(row, 'Type1Drug_name')
                type2_name = get_row_value(row, 'Type2Drug_name')
                if type1_name:
                    type1_names.add(type1_name)
                    if type2_name:
                        type2_mapping.setdefault(type1_name, set()).add(type2_name)

                # 收集持有人数据
                holder_name = get_row_value(row, 'ManufacturerHolder_name')
                if holder_name:
                    holder_names[holder_name] = get_row_value(row, 'ManufacturerHolder_abb')

                # 收集生产商数据
                manufacturer_name = get_row_value(row, 'Manufacturer_name')
                if manufacturer_name:
                    manufacturer_names[manufacturer_name] = get_row_value(row, 'Manufacturer_abb')

                # 保存行数据供后续使用
                all_rows.append({
                    'row': row,
                    'sheet_name': sheet_name,
                    'row_index': i,
                })
        
        logger.info(f"第一遍扫描完成：共 {len(all_rows)} 条有效数据")
        task_manager.update_progress(task_id, 15, f"解析完成，共 {len(all_rows)} 条有效数据，开始预创建关联数据...")

        # ========== 第二遍：批量预创建所有分类和关联数据 ==========
        logger.info("开始第二遍：预创建关联数据...")
        
        # 1. 批量创建一级分类
        with transaction.atomic():
            if type1_names:
                logger.info(f"创建一级分类: {type1_names}")
                Type1Drug.objects.bulk_create(
                    [Type1Drug(name=name) for name in type1_names],
                    ignore_conflicts=True
                )
        
        # 查询所有一级分类
        type1_objs = {t.name: t for t in Type1Drug.objects.filter(name__in=type1_names)}
        logger.info(f"一级分类查询完成: {len(type1_objs)} 个")

        # 2. 批量创建二级分类
        with transaction.atomic():
            type2_to_create = []
            for t1_name, t2_names in type2_mapping.items():
                t1 = type1_objs.get(t1_name)
                if t1:
                    for t2_name in t2_names:
                        type2_to_create.append(Type2Drug(name=t2_name, type1_drug=t1))
            
            if type2_to_create:
                logger.info(f"创建二级分类: {len(type2_to_create)} 个")
                Type2Drug.objects.bulk_create(type2_to_create, ignore_conflicts=True)
        
        # 查询所有二级分类
        type2_qs = Type2Drug.objects.filter(
            type1_drug__name__in=type1_names
        ).select_related('type1_drug')
        type2_objs = {}
        for t2 in type2_qs:
            key = (t2.type1_drug.name, t2.name)
            type2_objs[key] = t2
        logger.info(f"二级分类查询完成: {len(type2_objs)} 个")

        # 3. 批量创建上市许可持有人
        with transaction.atomic():
            if holder_names:
                logger.info(f"创建持有人: {len(holder_names)} 个")
                ManufacturerHolder.objects.bulk_create(
                    [
                        ManufacturerHolder(name=name, abbreviation=abb)
                        for name, abb in holder_names.items()
                    ],
                    ignore_conflicts=True
                )
        
        holder_objs = {h.name: h for h in ManufacturerHolder.objects.filter(name__in=holder_names.keys())}
        logger.info(f"持有人查询完成: {len(holder_objs)} 个")

        # 4. 批量创建生产商
        with transaction.atomic():
            if manufacturer_names:
                logger.info(f"创建生产商: {len(manufacturer_names)} 个")
                Manufacturer.objects.bulk_create(
                    [
                        Manufacturer(name=name, abbreviation=abb)
                        for name, abb in manufacturer_names.items()
                    ],
                    ignore_conflicts=True
                )
        
        manufacturer_objs = {m.name: m for m in Manufacturer.objects.filter(name__in=manufacturer_names.keys())}
        logger.info(f"生产商查询完成: {len(manufacturer_objs)} 个")
        
        task_manager.update_progress(task_id, 25, "关联数据预创建完成，开始导入药品...")

        # ========== 第三遍：逐个处理药品（每个药品独立事务） ==========
        logger.info(f"开始第三遍：导入药品数据，共 {len(all_rows)} 条...")
        created_drugs = []
        error_list = []
        skipped_duplicates = []
        processed_count = 0
        batch_size = max(1, len(all_rows) // 50)  # 每2%更新一次进度

        for idx, row_data in enumerate(all_rows):
            row = row_data['row']
            processed_count += 1
            
            # 更新进度
            if processed_count % batch_size == 0:
                progress = 25 + int((processed_count / len(all_rows)) * 70)
                task_manager.update_progress(
                    task_id, 
                    progress, 
                    f"正在导入... ({processed_count}/{len(all_rows)})",
                    {'processed': processed_count, 'total': len(all_rows)}
                )

            # 数据校验
            is_valid, validation_errors = validate_row_data(row)
            if not is_valid:
                error_list.append({
                    'drug_name': get_row_value(row, 'drug_name') or f'第{row_data["row_index"]+1}行',
                    'error': '; '.join(validation_errors)
                })
                continue

            # 唯一性校验
            is_unique, existing_drug = check_drug_uniqueness(row)
            if not is_unique:
                manufacturer_name = get_row_value(row, 'Manufacturer_name')
                skipped_duplicates.append({
                    'drug_name': get_row_value(row, 'drug_name'),
                    'manufacturer': manufacturer_name or get_row_value(row, 'Manufacturer_abb') or '未知厂商',
                    'approval_number': get_row_value(row, 'approval_number') or '',
                    'reason': '数据库中已存在相同药品名+批准文号+厂商的药品'
                })
                continue

            # 构建药品数据
            drug_data = {
                "drug_name": get_row_value(row, 'drug_name'),
                "drug_name_en": get_row_value(row, 'drug_name_en'),
                "trade_name": get_row_value(row, 'trade_name'),
                "trade_name_en": get_row_value(row, 'trade_name_en'),
                "medical_insurance": get_row_value(row, 'medical_insurance'),
                "jd_url": get_row_value(row, 'jd_url'),
                "category": get_row_value(row, 'category'),
                "specification": get_row_value(row, 'specification'),
                "dosage_form": get_row_value(row, 'dosage_form'),
                "administration_route": get_row_value(row, 'administration_route'),
                "active_ingredient": get_row_value(row, 'active_ingredient'),
                "active_ingredient_en": get_row_value(row, 'active_ingredient_en'),
                "approval_number": get_row_value(row, 'approval_number'),
                "approval_date": get_row_value(row, 'approval_date'),
                "atc_code": get_row_value(row, 'atc_code'),
                "market_status": get_row_value(row, 'market_status'),
                "family_use": get_row_value(row, 'family_use'),
                "indications": get_row_value(row, 'indications'),
                "description": get_row_value(row, 'description'),
            }

            try:
                with transaction.atomic():
                    # 关联二级分类
                    type1_name = get_row_value(row, 'Type1Drug_name')
                    type2_name = get_row_value(row, 'Type2Drug_name')
                    if type1_name and type2_name:
                        type2_obj = type2_objs.get((type1_name, type2_name))
                        if type2_obj:
                            drug_data["type2_drug"] = type2_obj

                    # 关联持有人
                    holder_name = get_row_value(row, 'ManufacturerHolder_name')
                    if holder_name:
                        holder_obj = holder_objs.get(holder_name)
                        if holder_obj:
                            drug_data["manufacturer_holder"] = holder_obj

                    # 关联生产商
                    manufacturer_name = get_row_value(row, 'Manufacturer_name')
                    if manufacturer_name:
                        manufacturer_obj = manufacturer_objs.get(manufacturer_name)
                        if manufacturer_obj:
                            drug_data["manufacturer"] = manufacturer_obj

                    # 方案C：使用药品名+厂商+批准文号作为唯一键
                    drug_name = drug_data['drug_name']
                    approval_number = drug_data.get('approval_number', '')
                    
                    # 构建唯一性查询条件（药品名 + 厂商 + 批准文号）
                    unique_query = Q(drug_name=drug_name)
                    if manufacturer_name:
                        unique_query &= Q(manufacturer__name=manufacturer_name)
                    if approval_number:
                        unique_query &= Q(approval_number=approval_number)
                    
                    # 查找是否已存在
                    existing_drug = Drug.objects.filter(unique_query).first()
                    
                    if existing_drug:
                        # 更新现有记录
                        for key, value in drug_data.items():
                            if key not in ['type2_drug', 'manufacturer_holder', 'manufacturer'] and value:
                                setattr(existing_drug, key, value)
                        # 单独处理外键关系
                        if 'type2_drug' in drug_data:
                            existing_drug.type2_drug = drug_data['type2_drug']
                        if 'manufacturer_holder' in drug_data:
                            existing_drug.manufacturer_holder = drug_data['manufacturer_holder']
                        if 'manufacturer' in drug_data:
                            existing_drug.manufacturer = drug_data['manufacturer']
                        existing_drug.save()
                        created_drugs.append(existing_drug.id)
                        logger.info(f"更新药品: {drug_name} (ID: {existing_drug.id})")
                    else:
                        # 创建新记录
                        drug = Drug.objects.create(**drug_data)
                        created_drugs.append(drug.id)
                        logger.info(f"创建药品: {drug_name} (ID: {drug.id})")

            except Exception as e:
                error_msg = f"处理药品 '{drug_data.get('drug_name')}' 失败: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                error_list.append({
                    'drug_name': drug_data.get('drug_name'),
                    'error': str(e)
                })

        # 构建返回结果
        result = {
            "success": True,
            "created_count": len(created_drugs),
            "skipped_count": len(skipped_duplicates),
            "skipped_duplicates": skipped_duplicates[:20] if skipped_duplicates else [],
            "total_rows": len(all_rows),
            "error_count": len(error_list),
            "error_list": error_list[:10] if error_list else [],
            "message": f"成功导入 {len(created_drugs)} 条药品记录，跳过 {len(skipped_duplicates)} 条重复，失败 {len(error_list)} 条",
        }
        
        logger.info(f"=== 导入任务 {task_id} 完成 ===")
        logger.info(f"结果: 成功创建 {len(created_drugs)} 条，跳过 {len(skipped_duplicates)} 条，失败 {len(error_list)} 条")
        if error_list:
            logger.warning(f"错误列表: {error_list[:5]}")
        
        task_manager.update_progress(task_id, 100, "导入完成", result)
        return result

    except Exception as e:
        logger.error(f"导入任务异常: {task_id}, {str(e)}")
        logger.error(traceback.format_exc())
        raise


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def async_import_drugs(request):
    """
    异步导入药品接口（后台线程处理）
    
    请求参数:
        - file: Excel文件
        - skip_duplicates: 是否跳过重复项（可选，默认true）
    
    返回:
        - task_id: 任务ID，用于查询任务状态
        - status: 任务状态
        - message: 状态消息
    
    使用流程:
        1. 调用此接口提交导入任务，立即返回任务ID
        2. 使用返回的 task_id 调用 /api/import_task_status/<task_id>/ 查询进度
        3. 轮询查询直到任务完成或失败
    """
    if not request.FILES.get("file"):
        return Response({"error": "未上传文件"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES["file"]
    
    # 检查文件类型
    if not file.name.lower().endswith((".xls", ".xlsx", ".xlsm", ".xlsb", ".odf", ".ods")):
        return Response(
            {"error": "文件类型错误，只允许上传 Excel 文件"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 读取文件数据（必须在主线程读取，因为 request.FILES 不能在后台线程访问）
        file_data = file.read()
        file_name = file.name
        skip_duplicates = request.POST.get('skip_duplicates', 'true').lower() == 'true'
        
        # 创建任务
        task_id = task_manager.create_task(task_type='import')
        
        # 启动后台线程处理导入
        run_import_in_thread(task_id, _process_import_task, file_data, file_name, skip_duplicates)
        
        return Response({
            "success": True,
            "task_id": task_id,
            "status": "pending",
            "message": "导入任务已提交，正在后台处理",
            "check_status_url": f"/api/import_task_status/{task_id}/"
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"创建导入任务失败: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({
            "error": f"创建导入任务失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_import_task_status(request, task_id):
    """
    查询导入任务状态
    
    返回任务执行进度、状态和结果
    """
    task_status = task_manager.get_task_status(task_id)
    
    if not task_status:
        return Response({
            "error": "任务不存在或已过期"
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        "success": True,
        "task": task_status
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_import_tasks(request):
    """
    获取导入任务列表（最近50个）
    """
    limit = int(request.query_params.get('limit', 50))
    tasks = task_manager.get_all_tasks(limit=limit)
    
    return Response({
        "success": True,
        "count": len(tasks),
        "tasks": [
            {
                'id': t['id'],
                'type': t['type'],
                'status': t['status'],
                'progress': t['progress'],
                'message': t['message'],
                'created_at': datetime.fromtimestamp(t['created_at']).isoformat(),
            }
            for t in tasks
        ]
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_import_task(request, task_id):
    """
    取消导入任务
    
    只能取消 pending 或 running 状态的任务
    """
    success = task_manager.cancel_task(task_id)
    
    if success:
        return Response({
            "success": True,
            "message": "任务已取消"
        })
    else:
        return Response({
            "error": "任务不存在或已完成，无法取消"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def async_batch_import_simple(request):
    """
    轻量级批量导入药品（后台线程处理）
    用于大批量数据导入，避免超时
    """
    if not request.FILES.get("file"):
        return Response({"error": "未上传文件"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES["file"]
    
    if not file.name.lower().endswith((".xls", ".xlsx")):
        return Response({"error": "只支持Excel文件"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        import pandas as pd
        
        # 读取文件数据
        file_data = file.read()
        file_name = file.name
        
        # 创建任务
        task_id = task_manager.create_task(task_type='import_simple')
        
        # 启动后台线程
        def process_simple_import(task_id: str, file_data: bytes, file_name: str):
            import io
            from django import db
            
            try:
                # 关键：关闭旧的数据库连接，确保后台线程使用自己的连接
                db.connections.close_all()
                
                task_manager.start_task(task_id)
                
                # 重建 DataFrame
                df = pd.read_excel(io.BytesIO(file_data)).fillna("")
                
                # 限制批次大小
                MAX_BATCH = 1000
                if len(df) > MAX_BATCH:
                    df = df.head(MAX_BATCH)
                
                task_manager.update_progress(task_id, 10, "正在预加载数据...")
                
                # 预加载所有分类和厂商
                type1_cache = {t.name: t for t in Type1Drug.objects.all()}
                type2_cache = {}
                for t2 in Type2Drug.objects.select_related('type1_drug').all():
                    type2_cache[(t2.type1_drug.name, t2.name)] = t2
                
                holder_cache = {h.name: h for h in ManufacturerHolder.objects.all()}
                manufacturer_cache = {m.name: m for m in Manufacturer.objects.all()}
                
                created_count = 0
                skipped_count = 0
                error_list = []
                
                batch_size = max(1, len(df) // 10)
                
                for idx, row in df.iterrows():
                    try:
                        drug_name = get_row_value(row, 'drug_name')
                        if not drug_name:
                            continue
                        
                        # 构建药品数据
                        drug_data = {
                            "drug_name": drug_name,
                            "drug_name_en": get_row_value(row, 'drug_name_en'),
                            "trade_name": get_row_value(row, 'trade_name'),
                            "trade_name_en": get_row_value(row, 'trade_name_en'),
                            "medical_insurance": get_row_value(row, 'medical_insurance'),
                            "jd_url": get_row_value(row, 'jd_url'),
                            "category": get_row_value(row, 'category'),
                            "specification": get_row_value(row, 'specification'),
                            "dosage_form": get_row_value(row, 'dosage_form'),
                            "administration_route": get_row_value(row, 'administration_route'),
                            "active_ingredient": get_row_value(row, 'active_ingredient'),
                            "active_ingredient_en": get_row_value(row, 'active_ingredient_en'),
                            "approval_number": get_row_value(row, 'approval_number'),
                            "approval_date": get_row_value(row, 'approval_date') or None,
                            "atc_code": get_row_value(row, 'atc_code'),
                            "market_status": get_row_value(row, 'market_status'),
                            "family_use": get_row_value(row, 'family_use'),
                            "indications": get_row_value(row, 'indications'),
                            "description": get_row_value(row, 'description'),
                        }
                        
                        # 关联分类
                        type1_name = get_row_value(row, 'Type1Drug_name')
                        type2_name = get_row_value(row, 'Type2Drug_name')
                        if type1_name and type2_name:
                            type2_obj = type2_cache.get((type1_name, type2_name))
                            if type2_obj:
                                drug_data["type2_drug"] = type2_obj
                        
                        # 关联持有人
                        holder_name = get_row_value(row, 'ManufacturerHolder_name')
                        if holder_name:
                            holder_obj = holder_cache.get(holder_name)
                            if holder_obj:
                                drug_data["manufacturer_holder"] = holder_obj
                        
                        # 关联生产商
                        manufacturer_name = get_row_value(row, 'Manufacturer_name')
                        if manufacturer_name:
                            manufacturer_obj = manufacturer_cache.get(manufacturer_name)
                            if manufacturer_obj:
                                drug_data["manufacturer"] = manufacturer_obj
                        
                        # 方案C：使用药品名+厂商+批准文号作为唯一键
                        approval_number = drug_data.get('approval_number', '')
                        
                        # 构建唯一性查询条件
                        unique_query = Q(drug_name=drug_name)
                        if manufacturer_name:
                            unique_query &= Q(manufacturer__name=manufacturer_name)
                        if approval_number:
                            unique_query &= Q(approval_number=approval_number)
                        
                        # 查找是否已存在
                        existing_drug = Drug.objects.filter(unique_query).first()
                        
                        if existing_drug:
                            # 更新现有记录
                            for key, value in drug_data.items():
                                if key not in ['type2_drug', 'manufacturer_holder', 'manufacturer'] and value:
                                    setattr(existing_drug, key, value)
                            if 'type2_drug' in drug_data:
                                existing_drug.type2_drug = drug_data['type2_drug']
                            if 'manufacturer_holder' in drug_data:
                                existing_drug.manufacturer_holder = drug_data['manufacturer_holder']
                            if 'manufacturer' in drug_data:
                                existing_drug.manufacturer = drug_data['manufacturer']
                            existing_drug.save()
                            created_count += 1
                        else:
                            # 创建新记录
                            Drug.objects.create(**drug_data)
                            created_count += 1
                        
                        # 更新进度
                        if (idx + 1) % batch_size == 0:
                            progress = 10 + int((idx + 1) / len(df) * 85)
                            task_manager.update_progress(
                                task_id, 
                                progress, 
                                f"正在导入... ({idx + 1}/{len(df)})"
                            )
                            
                    except Exception as e:
                        error_list.append({
                            'row': idx + 1,
                            'drug_name': drug_name if 'drug_name' in locals() else 'Unknown',
                            'error': str(e)
                        })
                
                result = {
                    "success": True,
                    "created_count": created_count,
                    "skipped_count": skipped_count,
                    "error_count": len(error_list),
                    "errors": error_list[:5],
                    "message": f"成功导入 {created_count} 条，跳过 {skipped_count} 条，失败 {len(error_list)} 条"
                }
                
                task_manager.complete_task(task_id, result)
                
            except Exception as e:
                logger.error(f"简单导入任务异常: {task_id}, {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                task_manager.fail_task(task_id, str(e))
            finally:
                # 任务完成后关闭数据库连接
                db.connections.close_all()
        
        # 启动线程
        thread = threading.Thread(
            target=process_simple_import, 
            args=(task_id, file_data, file_name),
            daemon=True
        )
        thread.start()
        
        return Response({
            "success": True,
            "task_id": task_id,
            "status": "pending",
            "message": "批量导入任务已提交，正在后台处理",
            "check_status_url": f"/api/import_task_status/{task_id}/"
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        return Response({
            "error": f"创建导入任务失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
