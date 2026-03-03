#!/usr/bin/env python
"""
医药宝测试数据生成脚本
使用方式: python generate_test_data.py
"""

import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpleserver.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"Django 初始化失败: {e}")
    print("请确保已安装依赖: pip install -r requirements.txt")
    sys.exit(1)

from syyb.models import Type1Drug, Type2Drug, ManufacturerHolder, Manufacturer, Drug
from susers.models import User
from django.db import transaction


def create_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    users_data = [
        {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@example.com',
            'name': '管理员',
            'mobile': '13800138000',
            'is_superuser': True,
            'is_staff': True,
            'sex': 1
        },
        {
            'username': 'testuser',
            'password': 'test123',
            'email': 'test@example.com',
            'name': '测试用户',
            'mobile': '13800138001',
            'is_superuser': False,
            'is_staff': False,
            'sex': 2
        },
        {
            'username': 'operator',
            'password': 'operator123',
            'email': 'operator@example.com',
            'name': '操作员',
            'mobile': '13800138002',
            'is_superuser': False,
            'is_staff': True,
            'sex': 1
        }
    ]
    
    created_count = 0
    for user_data in users_data:
        username = user_data['username']
        if not User.objects.filter(username=username).exists():
            password = user_data.pop('password')
            user = User.objects.create_user(**user_data)
            user.set_password(password)
            user.save()
            created_count += 1
            print(f"  创建用户: {username}")
        else:
            print(f"  用户已存在: {username}")
    
    print(f"用户创建完成，新增 {created_count} 个")
    return User.objects.first()


def create_categories():
    """创建药品分类数据"""
    print("\n创建药品分类...")
    
    categories = {
        '感冒用药': ['感冒发热', '咳嗽用药', '清热解毒'],
        '消化系统': ['肠胃用药', '肝胆用药', '止泻用药'],
        '心脑血管': ['高血压', '高血脂', '心脏病'],
        '维生素类': ['维生素A', '维生素B', '维生素C'],
        '外用药': ['皮肤用药', '眼部用药', '耳鼻喉'],
        '医疗器械': ['血压计', '血糖仪', '体温计'],
    }
    
    type1_list = []
    type2_list = []
    
    for type1_name, type2_names in categories.items():
        type1, created = Type1Drug.objects.get_or_create(name=type1_name)
        if created:
            print(f"  创建一级分类: {type1_name}")
        
        for type2_name in type2_names:
            type2, created = Type2Drug.objects.get_or_create(
                name=type2_name,
                type1_drug=type1
            )
            if created:
                print(f"    创建二级分类: {type2_name}")
                type2_list.append(type2)
    
    print(f"分类创建完成，共 {Type1Drug.objects.count()} 个一级分类，{Type2Drug.objects.count()} 个二级分类")
    return type2_list


def create_manufacturers():
    """创建厂商数据"""
    print("\n创建厂商数据...")
    
    holders_data = [
        {'name': '北京同仁堂股份有限公司', 'abbreviation': '同仁堂'},
        {'name': '云南白药集团股份有限公司', 'abbreviation': '云南白药'},
        {'name': '广州白云山医药集团股份有限公司', 'abbreviation': '白云山'},
        {'name': '哈药集团有限公司', 'abbreviation': '哈药'},
        {'name': '华润三九医药股份有限公司', 'abbreviation': '华润三九'},
        {'name': '修正药业集团股份有限公司', 'abbreviation': '修正药业'},
        {'name': '扬子江药业集团有限公司', 'abbreviation': '扬子江药业'},
        {'name': '江苏恒瑞医药股份有限公司', 'abbreviation': '恒瑞医药'},
    ]
    
    manufacturers_data = [
        {'name': '北京同仁堂制药有限公司', 'abbreviation': '同仁堂制药'},
        {'name': '云南白药集团文山七花有限责任公司', 'abbreviation': '文山七花'},
        {'name': '广州白云山制药总厂', 'abbreviation': '白云山总厂'},
        {'name': '哈药集团制药六厂', 'abbreviation': '哈药六厂'},
        {'name': '华润三九医药股份有限公司', 'abbreviation': '华润三九'},
        {'name': '修正药业集团长春高新制药有限公司', 'abbreviation': '修正高新'},
        {'name': '扬子江药业集团江苏紫龙药业有限公司', 'abbreviation': '紫龙药业'},
        {'name': '江苏恒瑞医药股份有限公司', 'abbreviation': '恒瑞医药'},
        {'name': '华北制药股份有限公司', 'abbreviation': '华北制药'},
        {'name': '东北制药集团股份有限公司', 'abbreviation': '东北制药'},
    ]
    
    holders = []
    for data in holders_data:
        obj, created = ManufacturerHolder.objects.get_or_create(**data)
        if created:
            print(f"  创建上市许可持有人: {data['name']}")
        holders.append(obj)
    
    manufacturers = []
    for data in manufacturers_data:
        obj, created = Manufacturer.objects.get_or_create(**data)
        if created:
            print(f"  创建生产厂商: {data['name']}")
        manufacturers.append(obj)
    
    print(f"厂商创建完成，共 {len(holders)} 个上市许可持有人，{len(manufacturers)} 个生产厂商")
    return holders, manufacturers


def create_drugs(type2_list, holders, manufacturers):
    """创建药品数据"""
    print("\n创建药品数据...")
    
    drugs_data = [
        {
            'drug_name': '感冒清热颗粒',
            'drug_name_en': 'Ganmao Qingre Granules',
            'trade_name': '同仁堂感冒清热颗粒',
            'trade_name_en': 'Tongrentang Ganmao Qingre Granules',
            'specification': '12g*10袋',
            'dosage_form': '颗粒剂',
            'administration_route': '口服',
            'active_ingredient': '荆芥穗、薄荷、防风、柴胡、紫苏叶、葛根、桔梗、苦杏仁、白芷、苦地丁、芦根',
            'approval_number': '国药准字Z11020361',
            'atc_code': 'R05X',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': True,
        },
        {
            'drug_name': '板蓝根颗粒',
            'drug_name_en': 'Banlangen Granules',
            'trade_name': '白云山板蓝根',
            'trade_name_en': 'Baiyunshan Banlangen',
            'specification': '10g*20袋',
            'dosage_form': '颗粒剂',
            'administration_route': '口服',
            'active_ingredient': '板蓝根',
            'approval_number': '国药准字Z44023485',
            'atc_code': 'J06A',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': True,
        },
        {
            'drug_name': '阿莫西林胶囊',
            'drug_name_en': 'Amoxicillin Capsules',
            'trade_name': '阿莫仙',
            'trade_name_en': 'Amoxil',
            'specification': '0.25g*24粒',
            'dosage_form': '胶囊剂',
            'administration_route': '口服',
            'active_ingredient': '阿莫西林',
            'approval_number': '国药准字H14020468',
            'atc_code': 'J01CA04',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '处方药',
            'is_hot': False,
        },
        {
            'drug_name': '布洛芬缓释胶囊',
            'drug_name_en': 'Ibuprofen Sustained-release Capsules',
            'trade_name': '芬必得',
            'trade_name_en': 'Fenbid',
            'specification': '0.3g*20粒',
            'dosage_form': '胶囊剂',
            'administration_route': '口服',
            'active_ingredient': '布洛芬',
            'approval_number': '国药准字H10900089',
            'atc_code': 'M01AE01',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': True,
        },
        {
            'drug_name': '复方甘草片',
            'drug_name_en': 'Compound Liquorice Tablets',
            'trade_name': '复方甘草片',
            'trade_name_en': 'Compound Liquorice Tablets',
            'specification': '100片',
            'dosage_form': '片剂',
            'administration_route': '口服含服',
            'active_ingredient': '甘草浸膏粉、阿片粉、樟脑、八角茴香油、苯甲酸钠',
            'approval_number': '国药准字H62020156',
            'atc_code': 'R05D',
            'medical_insurance': '乙类',
            'market_status': '上市',
            'family_use': '处方药',
            'is_hot': False,
        },
        {
            'drug_name': '维生素C片',
            'drug_name_en': 'Vitamin C Tablets',
            'trade_name': '力度伸',
            'trade_name_en': 'Redoxon',
            'specification': '100mg*30片',
            'dosage_form': '片剂',
            'administration_route': '口服',
            'active_ingredient': '维生素C',
            'approval_number': '国药准字H11021503',
            'atc_code': 'A11G',
            'medical_insurance': '乙类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': True,
        },
        {
            'drug_name': '红霉素软膏',
            'drug_name_en': 'Erythromycin Ointment',
            'trade_name': '红霉素软膏',
            'trade_name_en': 'Erythromycin Ointment',
            'specification': '1%*10g',
            'dosage_form': '软膏剂',
            'administration_route': '外用',
            'active_ingredient': '红霉素',
            'approval_number': '国药准字H42021008',
            'atc_code': 'D06A',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': False,
        },
        {
            'drug_name': '氯雷他定片',
            'drug_name_en': 'Loratadine Tablets',
            'trade_name': '开瑞坦',
            'trade_name_en': 'Clarityne',
            'specification': '10mg*6片',
            'dosage_form': '片剂',
            'administration_route': '口服',
            'active_ingredient': '氯雷他定',
            'approval_number': '国药准字H10970410',
            'atc_code': 'R06A',
            'medical_insurance': '乙类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': False,
        },
        {
            'drug_name': '硝苯地平缓释片',
            'drug_name_en': 'Nifedipine Sustained-release Tablets',
            'trade_name': '拜新同',
            'trade_name_en': 'Adalat',
            'specification': '30mg*7片',
            'dosage_form': '缓释片',
            'administration_route': '口服',
            'active_ingredient': '硝苯地平',
            'approval_number': '国药准字J20130115',
            'atc_code': 'C08C',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '处方药',
            'is_hot': False,
        },
        {
            'drug_name': '阿托伐他汀钙片',
            'drug_name_en': 'Atorvastatin Calcium Tablets',
            'trade_name': '立普妥',
            'trade_name_en': 'Lipitor',
            'specification': '20mg*7片',
            'dosage_form': '片剂',
            'administration_route': '口服',
            'active_ingredient': '阿托伐他汀钙',
            'approval_number': '国药准字J20130168',
            'atc_code': 'C10A',
            'medical_insurance': '乙类',
            'market_status': '上市',
            'family_use': '处方药',
            'is_hot': False,
        },
        {
            'drug_name': '氨溴索口服溶液',
            'drug_name_en': 'Ambroxol Oral Solution',
            'trade_name': '沐舒坦',
            'trade_name_en': 'Mucosolvan',
            'specification': '100ml:0.3g',
            'dosage_form': '口服溶液',
            'administration_route': '口服',
            'active_ingredient': '盐酸氨溴索',
            'approval_number': '国药准字H20031314',
            'atc_code': 'R05C',
            'medical_insurance': '乙类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': False,
        },
        {
            'drug_name': '蒙脱石散',
            'drug_name_en': 'Smectite Powder',
            'trade_name': '思密达',
            'trade_name_en': 'Smecta',
            'specification': '3g*10袋',
            'dosage_form': '散剂',
            'administration_route': '口服',
            'active_ingredient': '蒙脱石',
            'approval_number': '国药准字H20000690',
            'atc_code': 'A07B',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': True,
        },
        {
            'drug_name': '对乙酰氨基酚片',
            'drug_name_en': 'Paracetamol Tablets',
            'trade_name': '泰诺林',
            'trade_name_en': 'Tylenol',
            'specification': '0.5g*10片',
            'dosage_form': '片剂',
            'administration_route': '口服',
            'active_ingredient': '对乙酰氨基酚',
            'approval_number': '国药准字H31020393',
            'atc_code': 'N02B',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': True,
        },
        {
            'drug_name': '云南白药气雾剂',
            'drug_name_en': 'Yunnan Baiyao Aerosol',
            'trade_name': '云南白药',
            'trade_name_en': 'Yunnan Baiyao',
            'specification': '85g+60g',
            'dosage_form': '气雾剂',
            'administration_route': '外用',
            'active_ingredient': '草乌(制)等',
            'approval_number': '国药准字Z53021107',
            'atc_code': 'M02A',
            'medical_insurance': '乙类',
            'market_status': '上市',
            'family_use': '家庭常备',
            'is_hot': True,
        },
        {
            'drug_name': '二甲双胍片',
            'drug_name_en': 'Metformin Tablets',
            'trade_name': '格华止',
            'trade_name_en': 'Glucophage',
            'specification': '0.5g*20片',
            'dosage_form': '片剂',
            'administration_route': '口服',
            'active_ingredient': '盐酸二甲双胍',
            'approval_number': '国药准字H20023370',
            'atc_code': 'A10B',
            'medical_insurance': '甲类',
            'market_status': '上市',
            'family_use': '处方药',
            'is_hot': False,
        },
    ]
    
    # 随机分配分类、持有人和厂商
    import random
    from datetime import datetime, timedelta
    
    created_count = 0
    for i, drug_data in enumerate(drugs_data):
        atc_code = drug_data['atc_code']
        
        # 如果ATC代码已存在则跳过
        if Drug.objects.filter(atc_code=atc_code).exists():
            print(f"  药品已存在: {drug_data['drug_name']}")
            continue
        
        # 随机分配关系
        type2 = random.choice(type2_list) if type2_list else None
        holder = random.choice(holders) if holders else None
        manufacturer = random.choice(manufacturers) if manufacturers else None
        
        # 随机批准日期（近10年）
        days_ago = random.randint(365, 3650)
        approval_date = datetime.now().date() - timedelta(days=days_ago)
        
        drug = Drug.objects.create(
            drug_name=drug_data['drug_name'],
            drug_name_en=drug_data.get('drug_name_en'),
            trade_name=drug_data.get('trade_name'),
            trade_name_en=drug_data.get('trade_name_en'),
            specification=drug_data.get('specification'),
            dosage_form=drug_data.get('dosage_form'),
            administration_route=drug_data.get('administration_route'),
            active_ingredient=drug_data.get('active_ingredient'),
            active_ingredient_en=drug_data.get('active_ingredient_en'),
            approval_number=drug_data.get('approval_number'),
            approval_date=approval_date,
            atc_code=atc_code,
            medical_insurance=drug_data.get('medical_insurance'),
            market_status=drug_data.get('market_status'),
            family_use=drug_data.get('family_use'),
            is_hot=drug_data.get('is_hot', False),
            type2_drug=type2,
            manufacturer_holder=holder,
            manufacturer=manufacturer,
        )
        created_count += 1
        print(f"  创建药品: {drug.drug_name}")
    
    print(f"药品创建完成，新增 {created_count} 个")
    return created_count


def main():
    print("=" * 50)
    print("医药宝测试数据生成工具")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # 创建用户
            create_users()
            
            # 创建分类
            type2_list = create_categories()
            
            # 创建厂商
            holders, manufacturers = create_manufacturers()
            
            # 创建药品
            create_drugs(type2_list, holders, manufacturers)
            
        print("\n" + "=" * 50)
        print("测试数据生成完成！")
        print("=" * 50)
        print("\n登录信息：")
        print("  管理员: admin / admin123")
        print("  测试用户: testuser / test123")
        print("  操作员: operator / operator123")
        
    except Exception as e:
        print(f"\n生成数据时出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
