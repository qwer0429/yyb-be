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
    UserRegisterView, CustomTokenObtainPairView,
    UserManagementViewSet, CurrentUserView, ChangePasswordView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
#from sblogmd import urls as sblogmd_urls
#from scloud import urls as scloud_urls

app_name = 'susers'

# 创建路由器
router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user-management')

urlpatterns = [
    # 用户注册接口
    path('api/register/', UserRegisterView.as_view(), name='register'),
    
    # 自定义登录接口（返回用户信息）
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Token 刷新和验证
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # 当前用户信息管理
    path('api/me/', CurrentUserView.as_view(), name='current-user'),
    path('api/change_password/', ChangePasswordView.as_view(), name='change-password'),
]

urlpatterns += router.urls
