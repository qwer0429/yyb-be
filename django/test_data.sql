-- 医药宝测试数据 SQL
-- 使用方法: 导入到你的 MySQL 数据库

-- 清空现有数据（谨慎使用）
-- SET FOREIGN_KEY_CHECKS = 0;
-- TRUNCATE TABLE syyb_drug;
-- TRUNCATE TABLE syyb_type2drug;
-- TRUNCATE TABLE syyb_type1drug;
-- TRUNCATE TABLE syyb_manufacturer;
-- TRUNCATE TABLE syyb_manufacturerholder;
-- SET FOREIGN_KEY_CHECKS = 1;

-- 一级分类
INSERT INTO syyb_type1drug (id, name) VALUES 
(1, '感冒用药'),
(2, '消化系统'),
(3, '心脑血管'),
(4, '维生素类'),
(5, '外用药'),
(6, '医疗器械')
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 二级分类
INSERT INTO syyb_type2drug (id, name, type1_drug_id) VALUES 
(1, '感冒发热', 1),
(2, '咳嗽用药', 1),
(3, '清热解毒', 1),
(4, '肠胃用药', 2),
(5, '肝胆用药', 2),
(6, '止泻用药', 2),
(7, '高血压', 3),
(8, '高血脂', 3),
(9, '心脏病', 3),
(10, '维生素A', 4),
(11, '维生素B', 4),
(12, '维生素C', 4),
(13, '皮肤用药', 5),
(14, '眼部用药', 5),
(15, '耳鼻喉', 5)
ON DUPLICATE KEY UPDATE name = VALUES(name), type1_drug_id = VALUES(type1_drug_id);

-- 上市许可持有人
INSERT INTO syyb_manufacturerholder (id, name, abbreviation) VALUES 
(1, '北京同仁堂股份有限公司', '同仁堂'),
(2, '云南白药集团股份有限公司', '云南白药'),
(3, '广州白云山医药集团股份有限公司', '白云山'),
(4, '哈药集团有限公司', '哈药'),
(5, '华润三九医药股份有限公司', '华润三九'),
(6, '修正药业集团股份有限公司', '修正药业'),
(7, '扬子江药业集团有限公司', '扬子江药业'),
(8, '江苏恒瑞医药股份有限公司', '恒瑞医药')
ON DUPLICATE KEY UPDATE name = VALUES(name), abbreviation = VALUES(abbreviation);

-- 生产厂商
INSERT INTO syyb_manufacturer (id, name, abbreviation) VALUES 
(1, '北京同仁堂制药有限公司', '同仁堂制药'),
(2, '云南白药集团文山七花有限责任公司', '文山七花'),
(3, '广州白云山制药总厂', '白云山总厂'),
(4, '哈药集团制药六厂', '哈药六厂'),
(5, '华润三九医药股份有限公司', '华润三九'),
(6, '修正药业集团长春高新制药有限公司', '修正高新'),
(7, '扬子江药业集团江苏紫龙药业有限公司', '紫龙药业'),
(8, '江苏恒瑞医药股份有限公司', '恒瑞医药'),
(9, '华北制药股份有限公司', '华北制药'),
(10, '东北制药集团股份有限公司', '东北制药')
ON DUPLICATE KEY UPDATE name = VALUES(name), abbreviation = VALUES(abbreviation);

-- 药品数据
INSERT INTO syyb_drug (
    id, drug_name, drug_name_en, trade_name, trade_name_en, 
    specification, dosage_form, administration_route,
    active_ingredient, approval_number, atc_code,
    medical_insurance, market_status, family_use, is_hot,
    type2_drug_id, manufacturer_holder_id, manufacturer_id
) VALUES 
(1, '感冒清热颗粒', 'Ganmao Qingre Granules', '同仁堂感冒清热颗粒', 'Tongrentang Ganmao Qingre Granules',
 '12g*10袋', '颗粒剂', '口服', '荆芥穗、薄荷、防风、柴胡、紫苏叶、葛根、桔梗、苦杏仁、白芷、苦地丁、芦根',
 '国药准字Z11020361', 'R05X001', '甲类', '上市', '家庭常备', 1, 1, 1, 1),

(2, '板蓝根颗粒', 'Banlangen Granules', '白云山板蓝根', 'Baiyunshan Banlangen',
 '10g*20袋', '颗粒剂', '口服', '板蓝根',
 '国药准字Z44023485', 'J06A001', '甲类', '上市', '家庭常备', 1, 3, 3, 3),

(3, '阿莫西林胶囊', 'Amoxicillin Capsules', '阿莫仙', 'Amoxil',
 '0.25g*24粒', '胶囊剂', '口服', '阿莫西林',
 '国药准字H14020468', 'J01CA001', '甲类', '上市', '处方药', 0, 4, 4, 9),

(4, '布洛芬缓释胶囊', 'Ibuprofen Sustained-release Capsules', '芬必得', 'Fenbid',
 '0.3g*20粒', '胶囊剂', '口服', '布洛芬',
 '国药准字H10900089', 'M01AE001', '甲类', '上市', '家庭常备', 1, 1, 5, 5),

(5, '复方甘草片', 'Compound Liquorice Tablets', '复方甘草片', NULL,
 '100片', '片剂', '口服含服', '甘草浸膏粉、阿片粉、樟脑、八角茴香油、苯甲酸钠',
 '国药准字H62020156', 'R05D001', '乙类', '上市', '处方药', 0, 2, 6, 10),

(6, '维生素C片', 'Vitamin C Tablets', '力度伸', 'Redoxon',
 '100mg*30片', '片剂', '口服', '维生素C',
 '国药准字H11021503', 'A11G001', '乙类', '上市', '家庭常备', 1, 12, 5, 5),

(7, '红霉素软膏', 'Erythromycin Ointment', '红霉素软膏', NULL,
 '1%*10g', '软膏剂', '外用', '红霉素',
 '国药准字H42021008', 'D06A001', '甲类', '上市', '家庭常备', 0, 13, 4, 4),

(8, '氯雷他定片', 'Loratadine Tablets', '开瑞坦', 'Clarityne',
 '10mg*6片', '片剂', '口服', '氯雷他定',
 '国药准字H10970410', 'R06A001', '乙类', '上市', '家庭常备', 0, 15, 7, 7),

(9, '硝苯地平缓释片', 'Nifedipine Sustained-release Tablets', '拜新同', 'Adalat',
 '30mg*7片', '缓释片', '口服', '硝苯地平',
 '国药准字J20130115', 'C08C001', '甲类', '上市', '处方药', 0, 7, 8, 8),

(10, '阿托伐他汀钙片', 'Atorvastatin Calcium Tablets', '立普妥', 'Lipitor',
 '20mg*7片', '片剂', '口服', '阿托伐他汀钙',
 '国药准字J20130168', 'C10A001', '乙类', '上市', '处方药', 0, 8, 7, 7),

(11, '氨溴索口服溶液', 'Ambroxol Oral Solution', '沐舒坦', 'Mucosolvan',
 '100ml:0.3g', '口服溶液', '口服', '盐酸氨溴索',
 '国药准字H20031314', 'R05C001', '乙类', '上市', '家庭常备', 0, 2, 6, 6),

(12, '蒙脱石散', 'Smectite Powder', '思密达', 'Smecta',
 '3g*10袋', '散剂', '口服', '蒙脱石',
 '国药准字H20000690', 'A07B001', '甲类', '上市', '家庭常备', 1, 6, 5, 5),

(13, '对乙酰氨基酚片', 'Paracetamol Tablets', '泰诺林', 'Tylenol',
 '0.5g*10片', '片剂', '口服', '对乙酰氨基酚',
 '国药准字H31020393', 'N02B001', '甲类', '上市', '家庭常备', 1, 1, 5, 9),

(14, '云南白药气雾剂', 'Yunnan Baiyao Aerosol', '云南白药', NULL,
 '85g+60g', '气雾剂', '外用', '草乌(制)等',
 '国药准字Z53021107', 'M02A001', '乙类', '上市', '家庭常备', 1, 13, 2, 2),

(15, '二甲双胍片', 'Metformin Tablets', '格华止', 'Glucophage',
 '0.5g*20片', '片剂', '口服', '盐酸二甲双胍',
 '国药准字H20023370', 'A10B001', '甲类', '上市', '处方药', 0, 6, 3, 8)

ON DUPLICATE KEY UPDATE 
    drug_name = VALUES(drug_name),
    trade_name = VALUES(trade_name),
    specification = VALUES(specification);

-- 创建测试用户（密码需要 Django 加密，建议用脚本创建）
-- INSERT INTO susers_user (username, email, is_superuser, is_staff, is_active, name, mobile, sex) 
-- VALUES ('admin', 'admin@example.com', 1, 1, 1, '管理员', '13800138000', 1);
