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
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from susers.views import CustomTokenObtainPairView, UserRegisterView, CurrentUserView, ChangePasswordView
import simpleserver.settings as settings
from django.conf.urls.static import static
#from sblogmd import urls as sblogmd_urls
#from scloud import urls as scloud_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('susers/', include('susers.urls')),
    path('syyb/', include('syyb.urls')),
#    path('admin/', admin.site.urls),
    # DRF 提供的一系列身份认证的接口，用于在页面中认证身份，详情查阅DRF文档
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 用户注册接口
    path('api/register/', UserRegisterView.as_view(), name='register'),
    # 获取Token的接口（自定义，返回用户角色信息）
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 刷新Token有效期的接口
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 验证Token的有效性
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # 当前用户信息
    path('api/me/', CurrentUserView.as_view(), name='current-user'),
    # 修改密码
    path('api/change_password/', ChangePasswordView.as_view(), name='change-password'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
