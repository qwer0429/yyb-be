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
    'drug_name': {'required': True, 'label': '药品名', 'description': '药品通用名（必填）'},
    'drug_name_en': {'required': False, 'label': '药品名（英文）', 'description': '英文药品名'},
    'trade_name': {'required': False, 'label': '商品名', 'description': '商品名/品牌名'},
    'trade_name_en': {'required': False, 'label': '商品名（英文）', 'description': '英文商品名'},
    'specification': {'required': False, 'label': '规格', 'description': '如：0.25g*24粒'},
    'dosage_form': {'required': False, 'label': '剂型', 'description': '如：胶囊、片剂'},
    'administration_route': {'required': False, 'label': '给药途径', 'description': '如：口服、注射'},
    'active_ingredient': {'required': False, 'label': '活性成分', 'description': '主要成分'},
    'active_ingredient_en': {'required': False, 'label': '活性成分（英文）', 'description': '英文成分名'},
    'approval_number': {'required': False, 'label': '批准文号', 'description': '国药准字'},
    'approval_date': {'required': False, 'label': '批准日期', 'description': '格式：YYYY-MM-DD'},
    'atc_code': {'required': False, 'label': 'ATC代码', 'description': 'ATC分类代码'},
    'medical_insurance': {'required': False, 'label': '医保', 'description': '甲类/乙类/非医保'},
    'market_status': {'required': False, 'label': '上市销售状况', 'description': '在售/停产/退市'},
    'category': {'required': False, 'label': '收录类别', 'description': '分类信息'},
    'family_use': {'required': False, 'label': '家庭常用清单', 'description': '常用标记'},
    'jd_url': {'required': False, 'label': '京东链接', 'description': '电商链接'},
    'Type1Drug_name': {'required': False, 'label': '一级分类', 'description': '如：西药'},
    'Type2Drug_name': {'required': False, 'label': '二级分类', 'description': '如：抗生素'},
    'Manufacturer_name': {'required': False, 'label': '生产厂商', 'description': '生产厂家全称'},
    'Manufacturer_abb': {'required': False, 'label': '厂商简称', 'description': '厂商简称'},
    'ManufacturerHolder_name': {'required': False, 'label': '上市许可持有人', 'description': '持有人全称'},
    'ManufacturerHolder_abb': {'required': False, 'label': '持有人简称', 'description': '持有人简称'},
    'indications': {'required': False, 'label': '适用症状', 'description': '如：感冒、发热、头痛'},
    'description': {'required': False, 'label': '药品说明', 'description': '用法用量、注意事项等'},
    'drug_image_filename': {'required': False, 'label': '图片文件名', 'description': '图片文件名（如：drug001.jpg），需同时上传对应图片文件'},
}


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
        serializer = self.serializer_class(drugs, many=True)
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
    上传 Excel 文件，批量添加药品记录
    
    支持同时上传图片文件：
    - Excel 中填写图片文件名（如：drug001.jpg）
    - 同时上传对应的图片文件

    该接口提供了事务支持，确保数据的一致性。
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
            # 收集所有上传的图片文件 {文件名: 文件对象}
            image_files = {}
            for key, uploaded_file in request.FILES.items():
                if key != "file" and uploaded_file.name.lower().endswith(
                    ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
                ):
                    image_files[uploaded_file.name] = uploaded_file
            
            data = file.read()
            excel_file = pd.ExcelFile(io.BytesIO(data))
            userinfo_lst = []
            created_drugs = []
            image_success_count = 0
            image_fail_list = []

            # 使用事务确保数据一致性
            with transaction.atomic():
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

                        # 获取图片文件名
                        image_filename = get_row_value(row, 'drug_image_filename')

                        # 构建药品字典
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
                            "approval_date": get_row_value(row, 'approval_date'),
                            "atc_code": get_row_value(row, 'atc_code'),
                            "market_status": get_row_value(row, 'market_status'),
                            "family_use": get_row_value(row, 'family_use'),
                            "indications": get_row_value(row, 'indications'),
                            "description": get_row_value(row, 'description'),
                        }

                        try:

                            # 处理药品分类
                            type1_name = get_row_value(row, 'Type1Drug_name')
                            type2_name = get_row_value(row, 'Type2Drug_name')

                            # 获取或创建一级分类
                            type1_obj = None
                            if type1_name:
                                type1_obj, _ = Type1Drug.objects.get_or_create(
                                    name=type1_name
                                )

                            # 获取或创建二级分类（关联一级分类）
                            if type2_name and type1_obj:
                                type2_obj, _ = Type2Drug.objects.get_or_create(
                                    name=type2_name, type1_drug=type1_obj
                                )

                            if type2_obj:
                                drug_data["type2_drug"] = type2_obj

                            # holder_name = row.get('ManufacturerHolder_name', '')
                            # holder_obj = None
                            # if holder_name:
                            #     if ManufacturerHolder.objects.filter(name=holder_name).exists():
                            #         holder_obj = ManufacturerHolder.objects.filter(name=holder_name).first()
                            #     else:
                            #         holder_obj = ManufacturerHolder.objects.create(
                            #             name = holder_name,
                            #             abbreviation = row.get('ManufacturerHolder_abb', '')
                            #         )

                            holder_name = get_row_value(row, 'ManufacturerHolder_name')
                            if holder_name:
                                holder_obj, _ = (
                                    ManufacturerHolder.objects.get_or_create(
                                        name=holder_name,
                                        defaults={
                                            "name": holder_name,
                                            "abbreviation": get_row_value(row, 'ManufacturerHolder_abb'),
                                        },
                                    )
                                )

                            if holder_obj:
                                drug_data["manufacturer_holder"] = holder_obj

                            manufacturer_name = get_row_value(row, 'Manufacturer_name')
                            if manufacturer_name:
                                manufacturer_obj, _ = (
                                    Manufacturer.objects.get_or_create(
                                        name=manufacturer_name,
                                        defaults={
                                            "name": manufacturer_name,
                                            "abbreviation": get_row_value(row, 'Manufacturer_abb'),
                                        },
                                    )
                                )

                            if manufacturer_obj:
                                drug_data["manufacturer"] = manufacturer_obj

                            # # 检查药品是否已存在
                            # if Drug.objects.filter(
                            #     drug_name=drug_data['drug_name'],
                            #     approval_number=drug_data['approval_number']
                            # ).exists():
                            #     continue  # 跳过重复记录

                            # 创建药品并关联分类、持有人和生产商
                            drug, created = Drug.objects.update_or_create(
                                atc_code=drug_data["atc_code"],  # 查找条件
                                defaults=drug_data,  # 更新的字段
                            )

                            # drug = Drug.objects.create(
                            #     **drug_data,
                            #     type2_drug=type2_obj,
                            #     manufacturer_holder=holder_obj,
                            #     manufacturer=manufacturer_obj
                            # )

                            # 处理图片上传
                            if image_filename and image_filename in image_files:
                                try:
                                    from django.core.files.base import ContentFile
                                    image_file = image_files[image_filename]
                                    drug.drug_image.save(
                                        f"{drug.id}_{image_file.name}",
                                        ContentFile(image_file.read()),
                                        save=True
                                    )
                                    image_success_count += 1
                                except Exception as img_e:
                                    logger.error(f"图片上传失败 {image_filename}: {str(img_e)}")
                                    image_fail_list.append({
                                        'drug_name': drug_name,
                                        'filename': image_filename,
                                        'error': str(img_e)
                                    })

                            created_drugs.append(drug.id)
                            userinfo_lst.append(drug_data)
                        except Exception as e:
                            logger.error(f"处理过程中发生错误: {str(e)}")
                            logger.error(traceback.format_exc())

            # 构建返回消息
            message = f"成功导入 {len(created_drugs)} 条药品记录"
            if image_success_count > 0:
                message += f"，其中 {image_success_count} 条包含图片"
            if image_fail_list:
                message += f"，{len(image_fail_list)} 张图片上传失败"

            return JsonResponse(
                {
                    "success": True,
                    "created_count": len(created_drugs),
                    "total_rows": len(userinfo_lst),
                    "image_success_count": image_success_count,
                    "image_fail_count": len(image_fail_list),
                    "image_fail_list": image_fail_list,
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
