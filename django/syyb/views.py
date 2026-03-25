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
from rest_framework.pagination import PageNumberPagination

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
from rest_framework import viewsets, filters, permissions
from .serializers import (
    DrugSerializer,
    ManufacturerHolderSerializer,
    ManufacturerSerializer,
    Type1DrugSerializer,
    Type2DrugSerializer,
    Type1GetType2Serializer,
)
from .models import Drug, Manufacturer, ManufacturerHolder, Type1Drug, Type2Drug

from simpleserver.settings import (
    FSAT_YYB_TOKEN,
    FSAT_YYB_URL,
)

import os
import pandas as pd

import traceback

logger = logging.getLogger(__name__)


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


class CustomPagination(PageNumberPagination):
    page_size = 50  # 每页显示的记录数
    page_size_query_param = "page_size"  # 允许客户端通过参数指定每页大小
    max_page_size = 200  # 每页最大记录数


class DrugViewSet(viewsets.ModelViewSet):
    queryset = Drug.objects.all().order_by("-is_hot", "-id")
    serializer_class = DrugSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination


class Type1DrugViewSet(viewsets.ModelViewSet):
    queryset = Type1Drug.objects.all()
    serializer_class = Type1DrugSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination


class Type2DrugViewSet(viewsets.ModelViewSet):
    queryset = Type2Drug.objects.all()
    serializer_class = Type2DrugSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination


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

    需要提供 Excel 文件，文件名不限，sheet 名称不限。
    文件中每一行对应一个药品记录，字段名称见 models.py 中的 Drug 模型

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
            data = file.read()
            excel_file = pd.ExcelFile(io.BytesIO(data))
            userinfo_lst = []
            created_drugs = []

            # 使用事务确保数据一致性
            with transaction.atomic():
                for sheet_name in excel_file.sheet_names:
                    df = excel_file.parse(sheet_name).fillna("")

                    for i in range(1, len(df)):
                        row = df.iloc[i]
                        # 检查药品名称是否为空
                        if not row.get("drug_name") or not isinstance(
                            row["drug_name"], str
                        ):
                            continue  # 跳过空行

                        # # 处理日期字段
                        # approval_date = None
                        # if row.get('approval_date'):
                        #     # 处理多种日期格式
                        #     if isinstance(row['approval_date'], pd.Timestamp):
                        #         approval_date = row['approval_date'].to_pydatetime().date()
                        #     elif isinstance(row['approval_date'], str):
                        #         try:
                        #             approval_date = datetime.strptime(row['approval_date'], '%Y-%m-%d').date()
                        #         except:
                        #             try:
                        #                 approval_date = datetime.strptime(row['approval_date'], '%Y/%m/%d').date()
                        #             except:
                        #                 pass  # 保持为None

                        # 构建药品字典
                        drug_data = {
                            "drug_name": row["drug_name"],
                            "drug_name_en": row.get("drug_name_en", ""),
                            "trade_name": row.get("trade_name", ""),
                            "trade_name_en": row.get("trade_name_en", ""),
                            "medical_insurance": row.get("medical_insurance", ""),
                            "jd_url": row.get("jd_url", ""),
                            "category": row.get("category", ""),
                            "specification": row.get("specification", ""),
                            "dosage_form": row.get("dosage_form", ""),
                            "administration_route": row.get("administration_route", ""),
                            "active_ingredient": row.get("active_ingredient", ""),
                            "active_ingredient_en": row.get("active_ingredient_en", ""),
                            "approval_number": row.get("approval_number", ""),
                            "approval_date": row.get("approval_date", ""),
                            "atc_code": row.get("atc_code", ""),
                            "market_status": row.get("market_status", ""),
                            "family_use": row.get("family_use", ""),
                        }

                        try:

                            # 处理药品分类
                            type1_name = row.get("Type1Drug_name", "")
                            type2_name = row.get("Type2Drug_name", "")

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

                            holder_name = row.get("ManufacturerHolder_name", "")
                            if holder_name:
                                holder_obj, _ = (
                                    ManufacturerHolder.objects.get_or_create(
                                        name=holder_name,
                                        defaults={
                                            "name": row.get(
                                                "ManufacturerHolder_name", ""
                                            ),
                                            "abbreviation": row.get(
                                                "ManufacturerHolder_abb", ""
                                            ),
                                        },
                                    )
                                )

                            if holder_obj:
                                drug_data["manufacturer_holder"] = holder_obj

                            manufacturer_name = row.get("Manufacturer_name", "")
                            if manufacturer_name:
                                manufacturer_obj, _ = (
                                    Manufacturer.objects.get_or_create(
                                        name=manufacturer_name,
                                        defaults={
                                            "name": row.get("Manufacturer_name", ""),
                                            "abbreviation": row.get(
                                                "Manufacturer_abb", ""
                                            ),
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

                            created_drugs.append(drug.id)
                            userinfo_lst.append(drug_data)
                        except Exception as e:
                            logger.error(f"处理过程中发生错误: {str(e)}")
                            logger.error(traceback.format_exc())

            return JsonResponse(
                {
                    "success": True,
                    "created_count": len(created_drugs),
                    "total_rows": len(userinfo_lst),
                    "message": f"成功导入 {len(created_drugs)} 条药品记录",
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
