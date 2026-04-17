import pdb

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status

import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器 - 用于用户管理
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'mobile', 'email', 'sex', 'birthday', 
                  'is_admin', 'is_active', 'is_staff', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'name', 'mobile', 'email', 
                  'sex', 'is_admin', 'is_active']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    更新用户序列化器
    """
    password = serializers.CharField(write_only=True, required=False, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'name', 'mobile', 'email', 
                  'sex', 'birthday', 'is_admin', 'is_active']
        read_only_fields = ['id', 'username']
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 如果提供了密码，则更新密码
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化器 - 简化版
    """
    sex_display = serializers.CharField(source='get_sex_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'mobile', 'email', 'sex', 'sex_display',
                  'is_admin', 'is_active', 'date_joined', 'last_login']
