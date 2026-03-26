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
from django.contrib.auth.hashers import make_password
from .crypto_util import decrypt_password


# ==================== 用户注册视图 ====================

class UserRegisterView(APIView):
    """
    用户注册视图
    支持普通用户注册
    """
    permission_classes = []  # 允许未认证用户访问
    
    def post(self, request):
        data = request.data
        
        # 获取注册信息
        username = data.get('username', '').strip()
        password_encrypted = data.get('password', '').strip()
        password_confirm_encrypted = data.get('password_confirm', '').strip()
        mobile = data.get('mobile', '').strip()
        name = data.get('name', '').strip()
        
        # 验证必填字段
        if not username:
            return Response({'error': '用户名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not password_encrypted:
            return Response({'error': '密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 解密密码
        try:
            password = decrypt_password(password_encrypted)
            password_confirm = decrypt_password(password_confirm_encrypted)
        except Exception as e:
            logger.error(f'密码解密失败: {str(e)}')
            return Response({'error': '密码格式错误，请重新输入'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码长度
        if len(password) < 6:
            return Response({'error': '密码长度至少为6位'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证两次密码是否一致
        if password != password_confirm:
            return Response({'error': '两次输入的密码不一致'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户名是否已存在
        if User.objects.filter(username=username).exists():
            return Response({'error': '该用户名已被注册'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证手机号是否已存在（如果提供了手机号）
        if mobile and User.objects.filter(mobile=mobile).exists():
            return Response({'error': '该手机号已被注册'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建新用户
        try:
            user = User.objects.create(
                username=username,
                password=make_password(password),
                mobile=mobile if mobile else None,
                name=name if name else username,
                is_admin=False,  # 注册用户默认为普通用户
                is_active=True
            )
            
            # 生成Token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': '注册成功',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'mobile': user.mobile,
                    'is_admin': user.is_admin,
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'用户注册失败: {str(e)}')
            return Response({'error': '注册失败，请稍后重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== 自定义 Token 序列化器（返回用户角色信息） ====================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 Token 序列化器，添加用户角色信息
    支持加密密码传输
    """
    def validate(self, attrs):
        # 解密密码
        try:
            encrypted_password = attrs.get('password', '')
            if encrypted_password:
                attrs['password'] = decrypt_password(encrypted_password)
        except Exception as e:
            logger.error(f'登录密码解密失败: {str(e)}')
            raise Exception('密码格式错误，请重新输入')
        
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




