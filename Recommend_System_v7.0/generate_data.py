import csv
from datetime import datetime, timedelta
import random

def generate_purchase_data():
    # 用户组及其主要产品
    phone_users = [1, 4, 7, 10]
    tablet_users = [2, 5, 8]
    laptop_users = [3, 6, 9]
    
    # 产品组合
    phone_products = {
        'main': ['手机'],
        'essential': ['充电器', '手机壳', '移动电源'],
        'optional': ['耳机', '无线耳机', '蓝牙耳机', '手机支架']
    }
    
    tablet_products = {
        'main': ['平板'],
        'essential': ['触控笔', '平板保护套', '键盘'],
        'optional': ['无线鼠标', '外接显示器']
    }
    
    laptop_products = {
        'main': ['笔记本'],
        'essential': ['鼠标', '键盘', '笔记本包'],
        'optional': ['外接显示器', '机械键盘', '游戏鼠标', '无线鼠标', '耳机']
    }
    
    data = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 12, 31)  # 扩展到2026年以确保有足够数据
    current_date = start_date
    
    while current_date <= end_date:
        # 手机用户购买模式
        for user in phone_users:
            if current_date.day == 1:  # 每月初买主设备
                data.append([user, phone_products['main'][0], current_date.strftime('%Y-%m-%d')])
                # 必需配件（95%概率）
                for product in phone_products['essential']:
                    if random.random() < 0.95:
                        purchase_date = current_date + timedelta(days=random.randint(0, 3))
                        data.append([user, product, purchase_date.strftime('%Y-%m-%d')])
                # 可选配件（50%概率）
                for product in phone_products['optional']:
                    if random.random() < 0.5:
                        purchase_date = current_date + timedelta(days=random.randint(1, 7))
                        data.append([user, product, purchase_date.strftime('%Y-%m-%d')])
        
        # 平板用户购买模式
        for user in tablet_users:
            if current_date.day == 1:
                data.append([user, tablet_products['main'][0], current_date.strftime('%Y-%m-%d')])
                for product in tablet_products['essential']:
                    if random.random() < 0.95:
                        purchase_date = current_date + timedelta(days=random.randint(0, 3))
                        data.append([user, product, purchase_date.strftime('%Y-%m-%d')])
                for product in tablet_products['optional']:
                    if random.random() < 0.5:
                        purchase_date = current_date + timedelta(days=random.randint(1, 7))
                        data.append([user, product, purchase_date.strftime('%Y-%m-%d')])
        
        # 笔记本用户购买模式
        for user in laptop_users:
            if current_date.day == 1:
                data.append([user, laptop_products['main'][0], current_date.strftime('%Y-%m-%d')])
                for product in laptop_products['essential']:
                    if random.random() < 0.95:
                        purchase_date = current_date + timedelta(days=random.randint(0, 3))
                        data.append([user, product, purchase_date.strftime('%Y-%m-%d')])
                for product in laptop_products['optional']:
                    if random.random() < 0.5:
                        purchase_date = current_date + timedelta(days=random.randint(1, 7))
                        data.append([user, product, purchase_date.strftime('%Y-%m-%d')])
        
        # 每月15号的额外购买（补充消耗品）
        if current_date.day == 15:
            # 手机用户补充充电器和耳机
            for user in phone_users:
                if random.random() < 0.7:  # 70%概率补充
                    data.append([user, '充电器', current_date.strftime('%Y-%m-%d')])
                if random.random() < 0.3:  # 30%概率补充
                    data.append([user, random.choice(['耳机', '无线耳机', '蓝牙耳机']), current_date.strftime('%Y-%m-%d')])
            
            # 平板用户补充配件
            for user in tablet_users:
                if random.random() < 0.4:  # 40%概率补充
                    data.append([user, random.choice(['触控笔', '键盘']), current_date.strftime('%Y-%m-%d')])
            
            # 笔记本用户补充配件
            for user in laptop_users:
                if random.random() < 0.4:  # 40%概率补充
                    data.append([user, random.choice(['鼠标', '键盘']), current_date.strftime('%Y-%m-%d')])
        
        current_date += timedelta(days=1)
    
    # 按时间排序
    data.sort(key=lambda x: x[2])
    return data[:10000]  # 只返回前10000条记录

# 生成数据
purchase_data = generate_purchase_data()

# 写入CSV文件
with open('data/template.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'item_id', 'timestamp'])
    writer.writerows(purchase_data)

print(f'Generated {len(purchase_data)} records') 