from django.shortcuts import render
from django.http import HttpResponse
from django.forms.models import model_to_dict
# from django.http import StreamingHttpResponse
from django.http import FileResponse
from django.db.models import Q
from susers.api import token_required
from rest_framework import viewsets, permissions
from .models import User

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
import logging
logger = logging.getLogger(__name__)

import uuid
import json
import pdb
import re
import requests
import os
import subprocess

from rest_framework.permissions import BasePermission


# ==================== 自定义 Token 序列化器（返回用户角色信息） ====================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 Token 序列化器，添加用户角色信息
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        # 添加用户信息到响应
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'name': self.user.name,
            'mobile': self.user.mobile,
            'is_admin': self.user.is_admin,
            'is_staff': self.user.is_staff,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义 Token 视图，返回用户角色信息
    """
    serializer_class = CustomTokenObtainPairSerializer


# ==================== 权限控制类 ====================

class IsAdminUserCustom(BasePermission):
    """
    允许管理员访问的权限类
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsRegularUser(BasePermission):
    """
    允许普通用户访问的权限类
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_admin)




