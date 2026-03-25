from rest_framework import serializers
from .models import Drug, ManufacturerHolder, Manufacturer, Type1Drug, Type2Drug


class DrugSerializer(serializers.ModelSerializer):
    type1_drug = serializers.SerializerMethodField()

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
    manufacturer = serializers.PrimaryKeyRelatedField(
        queryset=Manufacturer.objects.all(), write_only=True, label="生产厂商ID"
    )

    class Meta:
        model = Drug
        fields = [
            'id', 'drug_name', 'drug_name_en', 'trade_name', 'trade_name_en', 'medical_insurance', 'jd_url', 'category',
            'type2_drug', 'type2_drug_name', 'type1_drug', 'specification', 'dosage_form', 'administration_route',
            'manufacturer_holder', 'manufacturer_holder_name', 'manufacturer_holder_abbreviation',
            'manufacturer', 'manufacturer_name', 'manufacturer_abbreviation', 'active_ingredient',
            'active_ingredient_en', 'approval_number', 'approval_date', 'atc_code', 'market_status',
            'drug_image', 'family_use', 'is_hot'
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

class ManufacturerHolderSerializer(serializers.ModelSerializer):# 定义一个只写的主键相关字段，用于接收药品的上市许可证持有人 ID
    class Meta:
        model = ManufacturerHolder
        fields = "__all__"


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"


class Type1DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type1Drug
        fields = "__all__"


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
        