"""
Web Application Module
This module implements the Flask web interface for the recommendation system.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from .recommendation import RecommendationSystem
import time

# 修改模板文件夹的路径
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

# 初始化推荐系统
rs = RecommendationSystem()

def load_product_categories():
    """从文件加载商品类别信息"""
    try:
        if os.path.exists('data/categories.csv'):
            categories_df = pd.read_csv('data/categories.csv', encoding='utf-8')
            return dict(zip(categories_df['item_id'], categories_df['category']))
    except Exception as e:
        print(f"加载类别文件时出错: {str(e)}")
    
    # 返回默认类别
    return {
        '手机': '移动设备',
        '平板': '移动设备',
        '笔记本': '电脑设备',
        '耳机': '音频配件',
        '无线耳机': '音频配件',
        '蓝牙耳机': '音频配件',
        '充电器': '电源配件',
        '移动电源': '电源配件',
        '键盘': '输入设备',
        '机械键盘': '输入设备',
        '鼠标': '输入设备',
        '无线鼠标': '输入设备',
        '游戏鼠标': '输入设备',
        '触控笔': '输入设备',
        '手机壳': '保护配件',
        '平板保护套': '保护配件',
        '笔记本包': '保护配件',
        '外接显示器': '显示设备',
        '手机支架': '支架配件'
    }

def save_product_categories(categories):
    """保存商品类别信息到文件"""
    try:
        categories_df = pd.DataFrame([
            {'item_id': item, 'category': category}
            for item, category in categories.items()
        ])
        os.makedirs('data', exist_ok=True)
        categories_df.to_csv('data/categories.csv', index=False, encoding='utf-8')
        print("类别信息已保存到文件")
    except Exception as e:
        print(f"保存类别文件时出错: {str(e)}")

# 加载商品类别
product_categories = load_product_categories()

# 加载示例数据
def load_initial_data():
    """加载初始数据"""
    try:
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # 构建 template.csv 的完整路径
        template_path = os.path.join(base_dir, 'data', 'template.csv')
        
        print(f"尝试加载数据文件: {template_path}")
        
        if os.path.exists(template_path):
            # 使用 utf-8 编码读取文件
            df = pd.read_csv(template_path, encoding='utf-8')
            print(f"成功加载数据文件，共 {len(df)} 条记录")
            print(f"唯一用户数: {df['user_id'].nunique()}")
            print(f"唯一商品数: {df['item_id'].nunique()}")
            return df
        else:
            print(f"警告：未找到数据文件 {template_path}")
            print("将使用默认数据")
            return pd.DataFrame({
                'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
                'item_id': ['手机', '耳机', '充电器', '手机', '平板', '键盘', '笔记本', '鼠标', '键盘'],
                'timestamp': pd.date_range(start='2024-01-01', periods=9)
            })
    except Exception as e:
        print(f"加载数据文件时出错: {str(e)}")
        return pd.DataFrame()

# 加载初始数据
df = load_initial_data()

# 初始化系统
rs.load_data(df)
rs.prepare_transaction_matrix()
rules = rs.generate_rules(min_support=0.05, min_confidence=0.3)

# 加载历史数据
def load_historical_data():
    try:
        # 读取template.csv文件
        df = pd.read_csv('data/template.csv')
        
        # 获取所有唯一用户ID并排序
        user_ids = sorted(df['user_id'].unique())
        
        # 获取商品类别
        product_categories = {}
        for _, row in df.iterrows():
            if row['item_id'] not in product_categories:
                product_categories[row['item_id']] = row['category']
        
        # 转换为购买历史记录格式
        purchase_history = []
        for _, row in df.iterrows():
            purchase_history.append({
                'user_id': int(row['user_id']),
                'product': row['item_id']
            })
        
        print(f"数据加载成功:")
        print(f"- 用户数量: {len(user_ids)}")
        print(f"- 商品数量: {len(product_categories)}")
        print(f"- 总记录数: {len(purchase_history)}")
        
        return purchase_history, user_ids, product_categories
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        return [], list(range(1, 11)), {}

# 初始化数据
purchase_history, user_ids, product_categories = load_historical_data()

@app.route('/')
def index():
    """渲染主页，传递用户ID列表和商品类别"""
    return render_template('index.html', 
                         user_ids=user_ids,
                         product_categories=product_categories)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        user_id = int(data.get('user_id'))
        
        # 获取用户历史购买记录
        historical_purchases = []
        for record in df.to_dict(orient='records'):
            if record['user_id'] == user_id:
                historical_purchases.append(record['item_id'])
        
        # 生成推荐
        recommendations = []
        start_time = time.time()
        
        if historical_purchases:
            for rule in rules.to_dict(orient='records'):
                if set(rule['antecedents']).issubset(set(historical_purchases)):
                    for item in rule['consequents']:
                        if item not in historical_purchases:
                            recommendations.append({
                                'product': item,
                                'confidence': rule['confidence'],
                                'support': rule['support'],
                                'lift': rule.get('lift', 0.0)
                            })
        
        # 计算性能指标
        processing_time = time.time() - start_time
        accuracy = len(recommendations) / len(rules) if rules is not None else 0
        
        return jsonify({
            'success': True,
            'historical_purchases': historical_purchases,
            'recommendations': recommendations,
            'metrics': {
                'accuracy': accuracy,
                'processing_time_ms': processing_time * 1000
            }
        })
        
    except Exception as e:
        print(f"获取推荐时出错：{str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/view_rules')
def view_rules():
    """查看关联规则"""
    # 创建规则列表并按类别和置信度排序
    categorized_rules = {}
    
    # 1. 按购买商品（前置项）的类别组织规则
    for _, rule in rules.iterrows():
        try:
            # 将 frozenset 转换为列表
            antecedents = list(rule['antecedents'])
            consequents = list(rule['consequents'])
            
            # 获取前置项（购买历史）的类别
            antecedent_categories = [product_categories[item] for item in antecedents]
            # 使用前置项的主要类别作为键（如果有多个类别，使用组合）
            main_category = "、".join(sorted(set(antecedent_categories)))
            
            # 获取后置项（推荐商品）的类别
            consequent_categories = [product_categories[item] for item in consequents]
            
            # 格式化商品名称列表
            antecedents_str = "、".join(str(item) for item in antecedents)
            consequents_str = "、".join(str(item) for item in consequents)
            consequent_categories_str = "、".join(sorted(set(consequent_categories)))
            
            # 添加规则信息
            rule_info = {
                'antecedents': antecedents,
                'consequents': consequents,
                'confidence': float(rule['confidence']),
                'support': float(rule['support']),
                'lift': float(rule['lift']),
                'description': {
                    'item_level': f"购买 {antecedents_str} 后，{float(rule['confidence']*100):.1f}% 的可能购买 {consequents_str}",
                    'category_level': f"购买{main_category}类商品后，{float(rule['confidence']*100):.1f}% 的可能购买{consequent_categories_str}类商品"
                }
            }
            
            # 将规则添加到对应的类别组合中
            if main_category not in categorized_rules:
                categorized_rules[main_category] = []
            categorized_rules[main_category].append(rule_info)
            
        except Exception as e:
            print(f"处理规则时出错: {str(e)}")
            continue
    
    # 2. 对每个类别内的规则按置信度排序
    sorted_rules = {}
    for category in sorted(categorized_rules.keys()):
        rules_list = categorized_rules[category]
        rules_list.sort(key=lambda x: (-x['confidence'], -x['support'], -x['lift']))
        sorted_rules[category] = rules_list
        
        # 打印调试信息
        print(f"\n类别: {category}")
        for rule in rules_list[:3]:  # 打印每个类别的前3条规则
            print(f"置信度: {rule['confidence']:.3f}, 支持度: {rule['support']:.3f}, 提升度: {rule['lift']:.3f}")
            print(f"商品级规则: {rule['description']['item_level']}")
            print(f"类别级规则: {rule['description']['category_level']}")
    
    return jsonify(sorted_rules)

def load_data_from_csv():
    """加载数据文件"""
    try:
        # 添加日志输出
        print("正在加载数据文件...")
        
        # 尝试从data目录加载
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'transactions.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            print(f"成功加载数据文件: {data_path}")
            print(f"数据集大小: {len(df)} 条记录")
            print(f"唯一用户数: {df['user_id'].nunique()}")
            print(f"唯一商品数: {df['item_id'].nunique()}")
            return df
        else:
            print(f"未找到数据文件: {data_path}")
            # 尝试在当前目录查找
            if os.path.exists('transactions.csv'):
                df = pd.read_csv('transactions.csv')
                print(f"从当前目录加载数据文件")
                print(f"数据集大小: {len(df)} 条记录")
                return df
            
        print("警告：未找到数据文件，将使用示例数据")
        return pd.DataFrame({
            'user_id': [1, 1, 2],
            'item_id': ['手机', '耳机', '平板'],
            'timestamp': ['2024-01-01', '2024-01-01', '2024-01-02']
        })
    except Exception as e:
        print(f"加载数据时出错: {str(e)}")
        return pd.DataFrame()

@app.route('/update_data', methods=['POST'])
def update_data():
    """更新数据"""
    global df, rs, rules, product_categories
    try:
        file = request.files['file']
        if file:
            # 保存上传的文件
            filename = 'transactions.csv'
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            
            # 加载新数据
            new_df = pd.read_csv(file_path)
            print(f"新上传的数据大小: {len(new_df)} 条记录")
            
            # 更新全局变量
            df = new_df
            
            # 更新商品类别
            new_items = set(df['item_id'].unique())
            for item in new_items:
                if item not in product_categories:
                    product_categories[item] = '未分类'
            save_product_categories(product_categories)
            
            # 重新初始化推荐系统
            rs.load_data(df)
            rs.prepare_transaction_matrix()
            
            # 使用更低的支持度和置信度以包含更多规则
            global rules
            rules = rs.generate_rules(min_support=0.05, min_confidence=0.2)
            
            print("系统更新状态：")
            print(f"- 数据记录数：{len(df)}")
            print(f"- 唯一用户数：{df['user_id'].nunique()}")
            print(f"- 唯一商品数：{df['item_id'].nunique()}")
            print(f"- 关联规则数：{len(rules) if rules is not None else 0}")
            
            return jsonify({
                'status': 'success',
                'message': f'数据更新成功，共 {len(df)} 条记录，{len(rules) if rules is not None else 0} 条规则'
            })
    except Exception as e:
        error_msg = f"数据更新失败: {str(e)}"
        print(error_msg)
        return jsonify({'status': 'error', 'message': error_msg})

@app.route('/update_category', methods=['POST'])
def update_category():
    """更新商品类别"""
    try:
        data = request.json
        item_id = data['item_id']
        new_category = data['category']
        
        # 更新类别
        global product_categories
        product_categories[item_id] = new_category
        save_product_categories(product_categories)
        
        # 重新生成规则
        rules = rs.generate_rules(min_support=0.05, min_confidence=0.3)
        
        return jsonify({'message': '类别更新成功'})
    except Exception as e:
        print(f"更新类别时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_lists')
def get_lists():
    """获取最新的用户列表和类别信息"""
    try:
        # 确保类别列表中没有重复
        unique_categories = sorted(set(product_categories.values()))
        
        # 确保所有商品都有对应的类别
        for item in df['item_id'].unique():
            if item not in product_categories:
                product_categories[item] = '未分类'
        
        return jsonify({
            'users': sorted(df['user_id'].unique()),
            'categories': product_categories,
            'all_categories': unique_categories
        })
    except Exception as e:
        print(f"获取列表时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/view_data')
def view_data():
    """查看数据表页面"""
    try:
        # 将数据转换为HTML表格，添加样式
        data_html = df.to_html(
            classes=['table', 'table-striped', 'table-hover'],
            index=False,
            border=0,
            justify='center'  # 居中对齐
        )
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>数据表查看</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .container {{ margin-top: 30px; }}
                .table {{ 
                    font-size: 14px;
                    width: 100%;
                    table-layout: fixed;
                }}
                .table th, .table td {{
                    text-align: center;
                    vertical-align: middle;
                    padding: 10px;
                }}
                .table th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                .table-responsive {{
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">数据表内容</h5>
                        <button onclick="window.print()" class="btn btn-secondary btn-sm">打印数据表</button>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            {data_html}
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"加载数据表时出错: {str(e)}", 500 