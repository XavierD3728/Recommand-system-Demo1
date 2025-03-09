"""
Recommendation System Module
This module implements the core functionality of the recommendation system.
"""

import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

class RecommendationSystem:
    def __init__(self):
        self.df = None
        self.transaction_matrix = None
        self.rules = None
        self.support_dict = {}  # 存储项集的支持度
        
    def load_data(self, df):
        """加载数据"""
        self.df = df
        
    def prepare_transaction_matrix(self):
        """
        准备交易矩阵
        将用户-商品购买记录转换为交易矩阵
        """
        # 按用户ID分组，获取每个用户的购买记录
        transactions = self.df.groupby('user_id')['item_id'].agg(list).reset_index()
        
        # 获取所有唯一商品
        all_items = sorted(self.df['item_id'].unique())
        
        # 创建交易矩阵
        matrix_data = []
        for _, row in transactions.iterrows():
            # 为每个商品创建一个布尔值，表示是否在该交易中出现
            transaction_vector = [1 if item in row['item_id'] else 0 for item in all_items]
            matrix_data.append(transaction_vector)
            
        # 创建DataFrame，列名为商品ID
        self.transaction_matrix = pd.DataFrame(matrix_data, columns=all_items)
        
        # 计算每个商品的支持度
        total_transactions = len(self.transaction_matrix)
        self.support_dict = {
            item: sum(self.transaction_matrix[item]) / total_transactions
            for item in all_items
        }
        
    def generate_rules(self, min_support=0.05, min_confidence=0.3):
        """
        生成关联规则
        参数:
            min_support: 最小支持度 (0-1)，默认值调整为0.05
            min_confidence: 最小置信度 (0-1)，默认值调整为0.3
        返回:
            包含关联规则的DataFrame
        """
        print(f"开始生成关联规则 (最小支持度: {min_support}, 最小置信度: {min_confidence})")
        print(f"交易矩阵大小: {self.transaction_matrix.shape}")
        
        # 使用Apriori算法找出频繁项集
        frequent_itemsets = apriori(
            self.transaction_matrix,
            min_support=min_support,
            use_colnames=True,
            max_len=3  # 限制项集大小，避免组合爆炸
        )
        
        if frequent_itemsets.empty:
            print(f"警告：未找到满足最小支持度 {min_support} 的频繁项集")
            return pd.DataFrame()
            
        print(f"找到 {len(frequent_itemsets)} 个频繁项集")
        
        # 生成关联规则
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=min_confidence
        )
        
        if rules.empty:
            print(f"警告：未找到满足最小置信度 {min_confidence} 的规则")
            return pd.DataFrame()
            
        # 计算调整后的提升度
        rules['adjusted_lift'] = rules.apply(
            lambda x: self._calculate_adjusted_lift(x['antecedents'], x['consequents'], 
                                                 x['support'], x['confidence']),
            axis=1
        )
        
        # 按照多个指标排序
        self.rules = rules.sort_values(
            ['confidence', 'adjusted_lift', 'support'],
            ascending=[False, False, False]
        )
        
        # 打印规则统计信息
        print("\n规则统计信息:")
        print(f"总规则数: {len(self.rules)}")
        print(f"置信度范围: {self.rules['confidence'].min():.3f} - {self.rules['confidence'].max():.3f}")
        print(f"支持度范围: {self.rules['support'].min():.3f} - {self.rules['support'].max():.3f}")
        print(f"提升度范围: {self.rules['lift'].min():.3f} - {self.rules['lift'].max():.3f}")
        
        # 打印一些示例规则
        print("\n示例规则:")
        for _, rule in self.rules.head(3).iterrows():
            ant = list(rule['antecedents'])
            cons = list(rule['consequents'])
            print(f"规则: {ant} -> {cons}")
            print(f"置信度: {rule['confidence']:.3f}")
            print(f"支持度: {rule['support']:.3f}")
            print(f"提升度: {rule['lift']:.3f}")
            print()
        
        return self.rules
    
    def _calculate_adjusted_lift(self, antecedents, consequents, support, confidence):
        """
        计算调整后的提升度，考虑项集大小的影响
        """
        # 计算前件和后件的基础支持度
        ant_support = np.mean([self.support_dict.get(item, 0) for item in antecedents])
        cons_support = np.mean([self.support_dict.get(item, 0) for item in consequents])
        
        # 避免除零错误
        if cons_support == 0:
            return 0
            
        # 计算调整后的提升度
        lift = confidence / cons_support
        
        # 根据项集大小进行调整
        size_penalty = 1 / (1 + len(antecedents) + len(consequents))
        adjusted_lift = lift * (1 + size_penalty)
        
        return adjusted_lift
    
    def get_recommendations(self, user_id, n_recommendations=3):
        """
        为指定用户生成推荐
        参数:
            user_id: 用户ID
            n_recommendations: 推荐商品数量
        返回:
            推荐商品列表
        """
        if self.rules is None or self.rules.empty:
            return []
            
        # 获取用户的购买历史
        user_history = set(self.df[self.df['user_id'] == user_id]['item_id'])
        
        if not user_history:
            print(f"用户 {user_id} 没有购买历史")
            return []
            
        # 根据用户历史筛选规则
        recommendations = []
        seen_items = set()
        
        # 按多个指标排序规则
        sorted_rules = self.rules.sort_values(
            ['confidence', 'adjusted_lift', 'support'],
            ascending=[False, False, False]
        )
        
        for _, rule in sorted_rules.iterrows():
            antecedents = set(rule['antecedents'])
            consequents = set(rule['consequents'])
            
            # 如果用户购买历史包含前置项，且后置项不在用户历史中
            if antecedents.issubset(user_history):
                for item in consequents:
                    if item not in user_history and item not in seen_items:
                        recommendations.append({
                            'item_id': item,
                            'confidence': float(rule['confidence']),
                            'support': float(rule['support']),
                            'lift': float(rule['adjusted_lift'])  # 使用调整后的提升度
                        })
                        seen_items.add(item)
                        
                        if len(recommendations) >= n_recommendations:
                            return recommendations
                            
        return recommendations 