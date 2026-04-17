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

from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, UserListSerializer


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
    登录成功后更新 last_login 时间
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # 登录成功后更新 last_login
        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.user
                from django.utils import timezone
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
        
        return response


# ==================== 权限控制类 ====================

class IsAdminUserCustom(BasePermission):
    """
    允许管理员访问的权限类
    检查 is_admin 或 is_superuser
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   (request.user.is_admin or request.user.is_superuser))


class IsRegularUser(BasePermission):
    """
    允许普通用户访问的权限类
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_admin)


# ==================== 用户管理视图集（仅管理员可用） ====================

class UserManagementViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集 - 仅管理员可访问
    提供用户的增删改查功能
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsAdminUserCustom]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        支持按用户名、姓名、手机号搜索
        """
        queryset = User.objects.all().order_by('-date_joined')
        
        # 搜索关键词
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(name__icontains=search) |
                Q(mobile__icontains=search) |
                Q(email__icontains=search)
            )
        
        # 按角色筛选
        role = self.request.query_params.get('role', '')
        if role == 'admin':
            queryset = queryset.filter(is_admin=True)
        elif role == 'user':
            queryset = queryset.filter(is_admin=False)
        
        # 按状态筛选
        is_active = self.request.query_params.get('is_active', '')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        重置用户密码为默认密码
        """
        user = self.get_object()
        default_password = request.data.get('password', '123456')
        
        user.set_password(default_password)
        user.need_reset = True
        user.save()
        
        return Response({
            'message': f'用户 {user.username} 的密码已重置',
            'user_id': user.id
        })
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        切换用户启用/禁用状态
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'用户 {user.username} 已{"启用" if user.is_active else "禁用"}',
            'is_active': user.is_active
        })
    
    @action(detail=False, methods=['delete'])
    def batch_delete(self, request):
        """
        批量删除用户
        """
        user_ids = request.data.get('user_ids', [])
        
        if not user_ids:
            return Response(
                {'error': '请选择要删除的用户'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 防止删除自己
        if request.user.id in user_ids:
            return Response(
                {'error': '不能删除当前登录的用户'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count = User.objects.filter(id__in=user_ids).delete()[0]
        
        return Response({
            'message': f'成功删除 {deleted_count} 个用户',
            'deleted_count': deleted_count
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取用户统计信息
        """
        total = User.objects.count()
        admin_count = User.objects.filter(is_admin=True).count()
        user_count = User.objects.filter(is_admin=False).count()
        active_count = User.objects.filter(is_active=True).count()
        inactive_count = User.objects.filter(is_active=False).count()
        
        # 今日新增用户
        from datetime import datetime, timedelta
        today = datetime.now().date()
        today_count = User.objects.filter(
            date_joined__date=today
        ).count()
        
        return Response({
            'total': total,
            'admin_count': admin_count,
            'user_count': user_count,
            'active_count': active_count,
            'inactive_count': inactive_count,
            'today_count': today_count
        })


# ==================== 当前用户信息管理视图 ====================

class CurrentUserView(APIView):
    """
    获取和更新当前登录用户信息
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """更新当前用户信息"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== 修改密码视图 ====================

class ChangePasswordView(APIView):
    """
    修改当前用户密码
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')
        
        # 验证旧密码
        if not request.user.check_password(old_password):
            return Response(
                {'error': '旧密码不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证新密码
        if len(new_password) < 6:
            return Response(
                {'error': '新密码长度至少为6位'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': '两次输入的新密码不一致'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 修改密码
        request.user.set_password(new_password)
        request.user.need_reset = False
        request.user.save()
        
        return Response({'message': '密码修改成功'})
