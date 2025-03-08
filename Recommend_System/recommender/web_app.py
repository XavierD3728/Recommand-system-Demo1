"""
Web Application Module
This module implements the Flask web interface for the recommendation system.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from .recommendation import RecommendationSystem

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
    try:
        if os.path.exists('data/template.csv'):
            return pd.read_csv('data/template.csv', encoding='utf-8')
    except Exception as e:
        print(f"加载数据文件时出错: {str(e)}")
    
    # 如果文件不存在，使用默认数据
    data = {
        'user_id':    [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'item_id':    ['手机', '耳机', '充电器', '手机', '平板', '键盘', '笔记本', '鼠标', '键盘'],
        'timestamp': pd.date_range(start='2024-01-01', periods=9)
    }
    return pd.DataFrame(data)

# 加载初始数据
df = load_initial_data()

# 初始化系统
rs.load_data(df)
rs.prepare_transaction_matrix()
rules = rs.generate_rules(min_support=0.05, min_confidence=0.3)

@app.route('/')
def home():
    """首页路由"""
    users = sorted(df['user_id'].unique())
    items = sorted(df['item_id'].unique())
    categories = sorted(set(product_categories.values()))
    return render_template('index.html', 
                         users=users, 
                         items=items, 
                         categories=categories,
                         product_categories=product_categories)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """获取推荐商品"""
    data = request.get_json()
    user_id = data.get('user_id')
    n_recommendations = data.get('n_recommendations', 3)  # 获取推荐数量参数，默认为3
    
    if not user_id:
        return jsonify({'error': '请提供用户ID'}), 400
    
    try:
        # 将user_id和n_recommendations转换为整数
        user_id = int(user_id)
        n_recommendations = int(n_recommendations)
        
        # 获取推荐
        recommendations = rs.get_recommendations(user_id, n_recommendations=n_recommendations)
        
        # 获取用户购买历史
        user_history = df[df['user_id'] == user_id]['item_id'].tolist()
        
        return jsonify({
            'recommendations': recommendations,
            'user_history': user_history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 读取并验证数据
        df_new = pd.read_csv(file)
        required_columns = ['user_id', 'item_id', 'timestamp']
        if not all(col in df_new.columns for col in required_columns):
            return jsonify({'error': '文件格式不正确'}), 400
        
        # 检查是否有新商品
        global df, rs, rules, product_categories
        new_items = set(df_new['item_id']) - set(product_categories.keys())
        
        if new_items:
            # 对于新商品，添加到"未分类"类别
            for item in new_items:
                product_categories[item] = '未分类'
            # 保存更新后的类别信息
            save_product_categories(product_categories)
        
        # 更新数据和规则
        df = df_new
        rs.load_data(df)
        rs.prepare_transaction_matrix()
        rules = rs.generate_rules(min_support=0.05, min_confidence=0.3)
        
        return jsonify({
            'message': '数据更新成功',
            'new_items': list(new_items) if new_items else []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        # 将数据转换为HTML表格
        data_html = df.to_html(
            classes=['table', 'table-striped', 'table-hover'],
            index=False,
            border=0
        )
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>数据表查看</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .container {{ margin-top: 30px; }}
                .table {{ font-size: 14px; }}
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