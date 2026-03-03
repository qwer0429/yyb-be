from django.db import models

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
    active_ingredient_en = models.CharField(max_length=255, blank=True, null=True, verbose_name="活性成分（英文）")
    approval_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="批准文号")
    approval_date = models.DateField(blank=True, null=True, verbose_name="批准日期")
    atc_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="ATC代码", unique=True)
    market_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="上市销售状况")
    drug_image = models.ImageField(upload_to='drug_images/', blank=True, null=True, verbose_name="药品图片")
    # drug_image = models.FileField(upload_to='drug_images/', blank=True, null=True, verbose_name="药品图片")
    family_use = models.CharField(max_length=100, blank=True, null=True, verbose_name="家庭常用清单")
    is_hot = models.BooleanField(default=False, verbose_name="是否为热门药品")


    def __str__(self):
        return f"{self.trade_name} ({self.type2_drug})"

    class Meta:
        verbose_name = "药品信息"
        verbose_name_plural = "药品信息"
        
        
