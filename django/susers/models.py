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



