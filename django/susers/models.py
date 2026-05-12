from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # 定义身份选项
    SEX_CHOICES = [
        (1, 'man'),
        (2, 'woman'),
        (3, 'secrecy'),
    ]
    # 手机号字段
    mobile = models.CharField(
        max_length=100,
        verbose_name='手机号',
        unique=True,  # 确保手机号是唯一的
        blank=True,  # 允许在表单中不填写
        null=True,  # 允许数据库中该字段为NULL
    )

    need_reset = models.BooleanField(default=False)
    is_default_password = models.BooleanField(default=False)
    name = models.CharField(max_length=150, blank=True)
    birthday = models.DateField(null=True, blank=True)
    sex = models.IntegerField(
        verbose_name='身份',
        choices=SEX_CHOICES,  # 使用上面定义的选择列表
        default=1,  # 默认值为1，代表学生
    )
    
    # 角色字段：True=管理员，False=普通用户
    is_admin = models.BooleanField(default=False, verbose_name='是否管理员')

    # 权限字段：存储用户可访问的系统列表
    # 例如：["user_portal", "admin_system", "smart_doctor"]
    permissions = models.JSONField(
        default=list,
        blank=True,
        verbose_name='可访问系统权限'
    )

    def get_accessible_systems(self):
        """
        获取用户可访问的系统列表
        默认普通用户可访问 user_portal
        管理员额外可访问 admin_system
        """
        systems = set(self.permissions) if self.permissions else set()
        systems.add('user_portal')  # 所有用户默认可以访问用户端
        
        if self.is_admin or self.is_superuser:
            systems.add('admin_system')  # 管理员可访问后台系统
            
        return list(systems)



