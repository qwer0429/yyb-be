from django.db import models
from django.conf import settings

class Type1Drug(models.Model):
    name = models.CharField(max_length=255, verbose_name="一级分类名称", unique=True)

    def __str__(self):
        return self.name

class Type2Drug(models.Model):
    name = models.CharField(max_length=255, verbose_name="二级分类名称")
    type1_drug = models.ForeignKey(Type1Drug, on_delete=models.CASCADE, verbose_name="所属一级分类")

    def __str__(self):
        return f"{self.type1_drug} - {self.name}"
    class Meta:
        unique_together = ('name', 'type1_drug')

class ManufacturerHolder(models.Model):
    name = models.CharField(max_length=255, verbose_name="上市许可持有人全称", unique=True)
    abbreviation = models.CharField(max_length=100, blank=True, null=True, verbose_name="简称")

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=255, verbose_name="生产厂商全称", unique=True)
    abbreviation = models.CharField(max_length=100, blank=True, null=True, verbose_name="简称")

    def __str__(self):
        return self.name

class Drug(models.Model):
    # 基本信息
    drug_name=models.CharField(max_length=255,verbose_name="药品名")
    drug_name_en=models.CharField(max_length=255, blank=True, null=True, verbose_name="药品名（英文）")
    trade_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="商品名")
    trade_name_en = models.CharField(max_length=255, blank=True, null=True, verbose_name="商品名（英文）")
    medical_insurance = models.CharField(max_length=255,null=True,verbose_name="医保")
    jd_url = models.TextField(blank=True, null=True,verbose_name="京东链接")
    category = models.CharField(max_length=255, blank=True, null=True, verbose_name="收录类别")

    # 分类信息
    type2_drug = models.ForeignKey(Type2Drug, blank=True, null=True, on_delete=models.CASCADE, verbose_name="二级分类")

    # 规格和剂型信息
    specification = models.CharField(max_length=255, blank=True, null=True, verbose_name="规格")
    dosage_form = models.CharField(max_length=100, blank=True, null=True, verbose_name="剂型")
    administration_route = models.CharField(max_length=100, blank=True, null=True, verbose_name="给药途径")

    # 持有人和生产商信息
    manufacturer_holder = models.ForeignKey(
        ManufacturerHolder,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="上市许可持有人"
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="生产厂商"
    )

    # 成分与批准信息
    active_ingredient = models.CharField(max_length=255, blank=True, null=True, verbose_name="活性成分")
    active_ingredient_en = models.CharField(max_length=1000, blank=True, null=True, verbose_name="活性成分（英文）")
    approval_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="批准文号")
    approval_date = models.DateField(blank=True, null=True, verbose_name="批准日期")
    atc_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="ATC代码")
    market_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="上市销售状况")
    drug_image = models.ImageField(upload_to='drug_images/', blank=True, null=True, verbose_name="药品图片")
    # drug_image = models.FileField(upload_to='drug_images/', blank=True, null=True, verbose_name="药品图片")
    family_use = models.CharField(max_length=100, blank=True, null=True, verbose_name="家庭常用清单")
    is_hot = models.BooleanField(default=False, verbose_name="是否为热门药品")
    
    # 新增字段：说明和适用症状
    description = models.TextField(blank=True, null=True, verbose_name="药品说明")
    indications = models.TextField(blank=True, null=True, verbose_name="适用症状")

    class Meta:
        verbose_name = "药品信息"
        verbose_name_plural = "药品信息"
        # 添加索引优化搜索性能
        indexes = [
            models.Index(fields=['drug_name'], name='idx_drug_name'),
            models.Index(fields=['trade_name'], name='idx_trade_name'),
            models.Index(fields=['atc_code'], name='idx_atc_code'),
            models.Index(fields=['is_hot'], name='idx_is_hot'),
            models.Index(fields=['type2_drug'], name='idx_type2_drug'),
        ]

    def __str__(self):
        return f"{self.trade_name} ({self.type2_drug})"


# ==================== 智慧药箱模块模型 ====================

class MedicineCabinet(models.Model):
    """
    用户药箱表
    每个用户可以有多个药箱（如：家庭药箱、旅行药箱等）
    """
    CABINET_TYPE_CHOICES = [
        ('home', '家庭药箱'),
        ('travel', '旅行药箱'),
        ('office', '办公室药箱'),
        ('other', '其他'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="所属用户",
        related_name='cabinets'
    )
    name = models.CharField(max_length=100, verbose_name="药箱名称")
    cabinet_type = models.CharField(
        max_length=20,
        choices=CABINET_TYPE_CHOICES,
        default='home',
        verbose_name="药箱类型"
    )
    description = models.TextField(blank=True, null=True, verbose_name="药箱描述")
    is_default = models.BooleanField(default=False, verbose_name="是否默认药箱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "药箱"
        verbose_name_plural = "药箱"
        # 每个用户的默认药箱只能有一个
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_cabinet_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class CabinetDrug(models.Model):
    """
    药箱-药品关系表
    记录药箱中的药品信息，包括库存数量、生产日期、有效期等
    """
    cabinet = models.ForeignKey(
        MedicineCabinet,
        on_delete=models.CASCADE,
        verbose_name="所属药箱",
        related_name='drugs'
    )
    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        verbose_name="药品",
        related_name='cabinet_drugs'
    )
    
    # 库存管理
    quantity = models.PositiveIntegerField(default=1, verbose_name="数量")
    unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="单位（片/粒/瓶等）")
    
    # 有效期管理
    production_date = models.DateField(blank=True, null=True, verbose_name="生产日期")
    valid_until = models.DateField(blank=True, null=True, verbose_name="有效期至")
    batch_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="批号")
    
    # 提醒设置
    remind_before_days = models.PositiveIntegerField(default=7, verbose_name="过期前提醒天数")
    is_reminded = models.BooleanField(default=False, verbose_name="是否已提醒")
    
    # 备注
    notes = models.TextField(blank=True, null=True, verbose_name="备注")
    
    # 时间戳
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "药箱药品"
        verbose_name_plural = "药箱药品"
        # 添加索引优化查询
        indexes = [
            models.Index(fields=['cabinet', 'drug'], name='idx_cabinet_drug'),
            models.Index(fields=['valid_until'], name='idx_valid_until'),
            models.Index(fields=['cabinet', 'valid_until'], name='idx_cabinet_valid'),
        ]

    def __str__(self):
        return f"{self.cabinet.name} - {self.drug.drug_name} ({self.quantity})"

    def is_expired(self):
        """检查药品是否已过期"""
        if self.valid_until:
            from datetime import date
            return self.valid_until < date.today()
        return False

    def is_expiring_soon(self):
        """检查药品是否即将过期"""
        if self.valid_until:
            from datetime import date, timedelta
            return (self.valid_until - date.today()).days <= self.remind_before_days
        return False

    def days_until_expiry(self):
        """返回距离过期还有多少天"""
        if self.valid_until:
            from datetime import date
            return (self.valid_until - date.today()).days
        return None
