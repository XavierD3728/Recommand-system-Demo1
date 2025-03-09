# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta

def generate_sample_data(num_transactions=1000):
    products = [
        '手机', '电脑', '平板', '耳机', '充电器', '移动电源', '手机壳', 
        '键盘', '鼠标', '显示器', '相机', '游戏机', '智能手表', '音响',
        '路由器', '数据线', '存储卡', '摄像头', '麦克风', '电池'
    ]
    
    # 生成过去30天内的随机时间
    def random_date():
        end = datetime.now()
        start = end - timedelta(days=30)
        return start + timedelta(
            seconds=random.randint(0, int((end - start).total_seconds()))
        )
    
    data = []
    for _ in range(num_transactions):
        user_id = random.randint(1, 10)  # 10个用户
        num_items = random.randint(1, 4)  # 每次购买1-4个商品
        items = random.sample(products, num_items)
        data.append({
            'user_id': user_id,
            'products': items,
            'timestamp': random_date().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # 按时间排序
    data.sort(key=lambda x: x['timestamp'])
    return data 

def generate_product_categories(num_products=1000):
    """生成大量商品和类别数据"""
    # 基础类别
    base_categories = {
        '电子设备': ['手机', '平板', '笔记本', '智能手表', '电子书阅读器', '相机', '游戏机'],
        '电子配件': ['耳机', '充电器', '触控笔', '键盘', '鼠标', '鼠标垫', '保护壳', '数据线'],
        '家用电器': ['电视', '冰箱', '洗衣机', '空调', '微波炉', '电饭煲', '吸尘器', '加湿器'],
        '服装': ['T恤', '牛仔裤', '夹克', '连衣裙', '运动鞋', '休闲鞋', '帽子', '袜子'],
        '图书': ['小说', '科普书', '教材', '漫画', '杂志', '词典', '艺术书', '历史书'],
        '食品': ['零食', '饮料', '水果', '蔬菜', '肉类', '海鲜', '乳制品', '谷物'],
        '家居': ['沙发', '床', '桌子', '椅子', '柜子', '灯具', '窗帘', '地毯'],
        '美妆': ['面霜', '洗面奶', '口红', '眼影', '粉底', '香水', '面膜', '防晒霜'],
        '运动': ['跑步机', '哑铃', '瑜伽垫', '篮球', '足球', '网球', '游泳用品', '健身器材'],
        '玩具': ['积木', '玩偶', '遥控车', '拼图', '棋牌', '模型', '电动玩具', '益智玩具']
    }
    
    # 扩展商品列表
    categories = {}
    product_to_category = {}
    
    for category, base_products in base_categories.items():
        products = []
        # 为每个基础商品创建多个变种
        for base_product in base_products:
            products.append(base_product)  # 添加基础商品
            # 添加变种商品
            for i in range(1, 13):  # 每个基础商品添加12个变种
                variant = f"{base_product} {i}型"
                products.append(variant)
        
        categories[category] = products
        
        # 更新反向映射
        for product in products:
            product_to_category[product] = category
    
    # 确保总商品数量达到1000
    all_products = list(product_to_category.keys())
    if len(all_products) < num_products:
        # 如果商品不足1000个，添加更多随机商品
        for i in range(len(all_products), num_products):
            category = random.choice(list(categories.keys()))
            product = f"商品{i+1}"
            categories[category].append(product)
            product_to_category[product] = category
    
    return categories, product_to_category

def generate_purchase_history(product_to_category, num_users=10, max_purchases=5):
    """生成用户购买历史"""
    all_products = list(product_to_category.keys())
    purchase_history = []
    
    for user_id in range(1, num_users + 1):
        # 每个用户有1-3条购买记录
        num_records = random.randint(1, 3)
        for _ in range(num_records):
            # 每条记录包含1-5个商品
            num_items = random.randint(1, max_purchases)
            items = random.sample(all_products, num_items)
            purchase_history.append({
                'user_id': user_id,
                'items': items
            })
    
    return purchase_history

def generate_association_rules(product_to_category, num_rules=15):
    """生成关联规则"""
    all_products = list(product_to_category.keys())
    rules = []
    
    for _ in range(num_rules):
        # 随机选择1-3个前置商品
        antecedent_size = random.randint(1, 3)
        antecedent = random.sample(all_products, antecedent_size)
        
        # 随机选择一个不在前置中的商品作为结果
        remaining_products = [p for p in all_products if p not in antecedent]
        if not remaining_products:
            continue
        consequent = random.choice(remaining_products)
        
        # 生成随机的置信度和支持度
        confidence = round(random.uniform(0.5, 1.0), 2)
        support = round(random.uniform(0.1, 0.5), 2)
        
        rules.append({
            'antecedent': antecedent,
            'consequent': consequent,
            'confidence': confidence,
            'support': support
        })
    
    return rules

def get_test_data():
    """获取测试数据"""
    categories, product_to_category = generate_product_categories(1000)
    
    return {
        'product_categories': product_to_category
    }

if __name__ == "__main__":
    # 测试数据生成
    data = get_test_data()
    print(f"生成的商品总数: {len(data['product_categories'])}")
    
    # 按类别统计商品数量
    category_counts = {}
    for product, category in data['product_categories'].items():
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
    
    print("\n各类别商品数量:")
    for category, count in category_counts.items():
        print(f"  {category}: {count}件") 