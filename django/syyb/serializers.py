from rest_framework import serializers
from .models import (
    Drug, ManufacturerHolder, Manufacturer, Type1Drug, Type2Drug,
    MedicineCabinet, CabinetDrug
)


class DrugListSerializer(serializers.ModelSerializer):
    """简化版药品列表序列化器，只返回列表展示需要的字段"""
    type2_drug_id = serializers.IntegerField(source='type2_drug.id', read_only=True, allow_null=True)
    type2_drug_name = serializers.CharField(source='type2_drug.name', read_only=True)
    type1_drug = serializers.CharField(source='type2_drug.type1_drug.name', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)
    manufacturer_abbreviation = serializers.CharField(source='manufacturer.abbreviation', read_only=True)
    manufacturer_id = serializers.IntegerField(source='manufacturer.id', read_only=True)
    manufacturer_holder_name = serializers.CharField(source='manufacturer_holder.name', read_only=True)
    manufacturer_holder_id = serializers.IntegerField(source='manufacturer_holder.id', read_only=True)
    drug_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Drug
        fields = [
            'id', 'drug_name', 'drug_name_en', 'trade_name', 'trade_name_en',
            'specification', 'dosage_form', 'medical_insurance',
            'type2_drug_id', 'type2_drug_name', 'type1_drug', 'manufacturer_name', 'manufacturer_id',
            'manufacturer_abbreviation', 'manufacturer_holder_name', 'manufacturer_holder_id',
            'approval_number', 'approval_date', 'atc_code',
            'market_status', 'drug_image', 'family_use', 'is_hot', 'indications', 'description'
        ]
    
    def get_drug_image(self, obj):
        """返回完整的图片URL"""
        if obj.drug_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.drug_image.url)
            return obj.drug_image.url
        return None


class DrugSerializer(serializers.ModelSerializer):
    type1_drug = serializers.SerializerMethodField()

    # 二级分类ID（用于前端筛选）
    type2_drug_id = serializers.IntegerField(source='type2_drug.id', read_only=True, allow_null=True)
    # 二级分类显示名称及简称
    type2_drug_name = serializers.SerializerMethodField(read_only=True, label="二级分类")
    type2_drug = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Type2Drug.objects.all(), label="二级分类id", required=False, allow_null=True
    )

    # 上市许可持有人显示名称及简称
    manufacturer_holder_name = serializers.CharField(
        source='manufacturer_holder.name', read_only=True, label="上市许可持有人全称"
    )
    manufacturer_holder_abbreviation = serializers.CharField(
        source='manufacturer_holder.abbreviation', read_only=True, label="上市许可持有人简称"
    )
    manufacturer_holder = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=ManufacturerHolder.objects.all(), label="上市许可持有人id", required=False, allow_null=True
    )

    # 生产厂商显示名称及简称
    manufacturer_name = serializers.CharField(
        source='manufacturer.name', read_only=True, label="生产厂商全称"
    )
    manufacturer_abbreviation = serializers.CharField(
        source='manufacturer.abbreviation', read_only=True, label="生产厂商简称"
    )
    # 用于读取厂商ID（编辑时显示）
    manufacturer_id = serializers.IntegerField(
        source='manufacturer.id', read_only=True, label="生产厂商ID"
    )
    # 用于写入厂商ID
    manufacturer = serializers.PrimaryKeyRelatedField(
        queryset=Manufacturer.objects.all(), write_only=True, label="生产厂商ID", required=False, allow_null=True
    )
    
    # 图片字段返回完整URL
    drug_image = serializers.SerializerMethodField()

    class Meta:
        model = Drug
        fields = [
            'id', 'drug_name', 'drug_name_en', 'trade_name', 'trade_name_en', 'medical_insurance', 'jd_url', 'category',
            'type2_drug', 'type2_drug_id', 'type2_drug_name', 'type1_drug', 'specification', 'dosage_form', 'administration_route',
            'manufacturer_holder', 'manufacturer_holder_name', 'manufacturer_holder_abbreviation',
            'manufacturer', 'manufacturer_id', 'manufacturer_name', 'manufacturer_abbreviation', 'active_ingredient',
            'active_ingredient_en', 'approval_number', 'approval_date', 'atc_code', 'market_status',
            'drug_image', 'family_use', 'is_hot', 'description', 'indications'
        ]
        extra_kwargs = {
            'type2_drug': {'write_only': True},
            'manufacturer_holder': {'write_only': True},
            'manufacturer': {'write_only': True},
        }

    def get_type1_drug(self, obj):
        if obj.type2_drug and obj.type2_drug.type1_drug:
            return obj.type2_drug.type1_drug.name
        return None
    
    def get_type2_drug_name(self, obj):
        if obj.type2_drug:
            return obj.type2_drug.name
        return None
    
    def get_drug_image(self, obj):
        """返回完整的图片URL"""
        if obj.drug_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.drug_image.url)
            return obj.drug_image.url
        return None

class ManufacturerHolderSerializer(serializers.ModelSerializer):# 定义一个只写的主键相关字段，用于接收药品的上市许可证持有人 ID
    class Meta:
        model = ManufacturerHolder
        fields = "__all__"


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"


class Type1DrugSerializer(serializers.ModelSerializer):
    """一级分类序列化器 - 包含子分类数量"""
    type2_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Type1Drug
        fields = ['id', 'name', 'type2_count']
    
    def get_type2_count(self, obj):
        return obj.type2drug_set.count()


class Type2DrugSerializer(serializers.ModelSerializer):
    # 添加drugs_count字段用于统计二级分类下的药品数量
    drugs_count = serializers.SerializerMethodField(
        read_only = True
    )
    class Meta:
        model = Type2Drug
        fields = "__all__"
    
    def get_drugs_count(self, obj):
        # return Drug.objects.filter(type2_drug = obj).count()
        # 优化查询
        return obj.drug_set.count()
    
class Type1GetType2Serializer(serializers.ModelSerializer):
    """
    序列化一级分类下的二级分类
    """
    class Meta:
        model = Type2Drug
        fields = ['id', 'name']  # 只序列化二级分类的id和name字段


# ==================== 智慧药箱模块序列化器 ====================

class MedicineCabinetSerializer(serializers.ModelSerializer):
    """药箱序列化器"""
    drug_count = serializers.SerializerMethodField(read_only=True, label="药品数量")
    
    class Meta:
        model = MedicineCabinet
        fields = ['id', 'name', 'cabinet_type', 'description', 'is_default', 'drug_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_drug_count(self, obj):
        return obj.drugs.count()


class CabinetDrugListSerializer(serializers.ModelSerializer):
    """药箱药品列表序列化器（用于展示）"""
    drug_name = serializers.CharField(source='drug.drug_name', read_only=True)
    drug_trade_name = serializers.CharField(source='drug.trade_name', read_only=True)
    drug_image = serializers.SerializerMethodField()
    drug_specification = serializers.CharField(source='drug.specification', read_only=True)
    drug_dosage_form = serializers.CharField(source='drug.dosage_form', read_only=True)
    manufacturer_name = serializers.CharField(source='drug.manufacturer.name', read_only=True)
    
    # 过期状态
    is_expired = serializers.SerializerMethodField(read_only=True)
    is_expiring_soon = serializers.SerializerMethodField(read_only=True)
    days_until_expiry = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CabinetDrug
        fields = [
            'id', 'drug', 'drug_name', 'drug_trade_name', 'drug_image', 'drug_specification',
            'drug_dosage_form', 'manufacturer_name', 'quantity', 'unit', 'production_date',
            'valid_until', 'batch_number', 'remind_before_days', 'is_reminded', 'notes',
            'is_expired', 'is_expiring_soon', 'days_until_expiry', 'added_at', 'updated_at'
        ]
        read_only_fields = ['added_at', 'updated_at']
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def get_is_expiring_soon(self, obj):
        return obj.is_expiring_soon()
    
    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry()
    
    def get_drug_image(self, obj):
        """返回完整的图片URL"""
        if obj.drug and obj.drug.drug_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.drug.drug_image.url)
            return obj.drug.drug_image.url
        return None


class CabinetDrugCreateSerializer(serializers.ModelSerializer):
    """药箱药品创建/更新序列化器"""
    class Meta:
        model = CabinetDrug
        fields = [
            'id', 'cabinet', 'drug', 'quantity', 'unit', 'production_date',
            'valid_until', 'batch_number', 'remind_before_days', 'notes'
        ]
    
    def validate(self, data):
        # 验证有效期必须晚于生产日期
        production_date = data.get('production_date')
        valid_until = data.get('valid_until')
        
        if production_date and valid_until and valid_until <= production_date:
            raise serializers.ValidationError("有效期必须晚于生产日期")
        
        return data


class CabinetDrugUpdateSerializer(serializers.ModelSerializer):
    """药箱药品更新序列化器（部分更新）"""
    class Meta:
        model = CabinetDrug
        fields = ['quantity', 'unit', 'production_date', 'valid_until', 'batch_number', 'remind_before_days', 'notes']
        partial = True


class ExpiringDrugSerializer(serializers.Serializer):
    """即将过期药品统计序列化器"""
    expiring_count = serializers.IntegerField()
    expired_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    expiring_drugs = CabinetDrugListSerializer(many=True)
        