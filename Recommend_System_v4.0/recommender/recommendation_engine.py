# -*- coding: utf-8 -*-
from collections import Counter
import random
import time

class MetricsTracker:
    """跟踪和计算推荐系统的性能指标"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置所有指标"""
        self.start_time = None
        self.end_time = None
        self.processing_time = 0
        self.accuracy = 0
        self.total_rules = 0
        self.matched_rules = 0
    
    def start_tracking(self):
        """开始计时"""
        self.start_time = time.time()
    
    def stop_tracking(self):
        """停止计时并计算处理时间"""
        self.end_time = time.time()
        self.processing_time = self.end_time - self.start_time
    
    def calculate_accuracy(self, recommendations, total_rules):
        """计算推荐准确率"""
        self.total_rules = total_rules
        self.matched_rules = len(recommendations)
        self.accuracy = self.matched_rules / self.total_rules if self.total_rules > 0 else 0
    
    def get_metrics(self):
        """获取所有指标"""
        return {
            'accuracy': self.accuracy,
            'processing_time_ms': self.processing_time * 1000,
            'matched_rules': self.matched_rules,
            'total_rules': self.total_rules
        }

class RecommendationEngine:
    """推荐引擎，基于关联规则生成推荐"""
    
    def __init__(self, product_categories, purchase_history, association_rules):
        self.product_categories = product_categories
        self.purchase_history = purchase_history
        self.association_rules = association_rules
        self.metrics_tracker = MetricsTracker()
    
    def get_user_history(self, user_id):
        """获取用户的历史购买记录"""
        user_items = []
        for record in self.purchase_history:
            if record['user_id'] == user_id:
                user_items.extend(record['items'])
        return list(set(user_items))  # 去重
    
    def generate_recommendations(self, user_id):
        """为用户生成推荐"""
        # 重置并开始跟踪指标
        self.metrics_tracker.reset()
        self.metrics_tracker.start_tracking()
        
        try:
            # 获取用户历史购买记录
            user_history = self.get_user_history(user_id)
            
            # 根据关联规则生成推荐
            recommendations = []
            for rule in self.association_rules:
                # 如果用户历史包含规则的前置条件，则推荐结果
                if set(rule['antecedent']).issubset(set(user_history)):
                    # 检查推荐的商品是否已经在用户历史中
                    if rule['consequent'] not in user_history:
                        recommendations.append({
                            'product': rule['consequent'],
                            'confidence': rule['confidence'],
                            'support': rule['support'],
                            'category': self.product_categories.get(rule['consequent'], '未分类')
                        })
            
            # 按置信度排序
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            
            # 停止跟踪并计算指标
            self.metrics_tracker.stop_tracking()
            self.metrics_tracker.calculate_accuracy(recommendations, len(self.association_rules))
            
            return {
                'success': True,
                'recommendations': recommendations,
                'historical_purchases': user_history,
                'metrics': self.metrics_tracker.get_metrics()
            }
            
        except Exception as e:
            # 发生错误时也停止跟踪
            self.metrics_tracker.stop_tracking()
            
            return {
                'success': False,
                'error': str(e),
                'recommendations': [],
                'historical_purchases': [],
                'metrics': self.metrics_tracker.get_metrics()
            }

    def train(self, data):
        self.data = data
        self._build_associations()
        
    def _build_associations(self):
        # 构建商品关联关系
        for transaction in self.data:
            products = transaction['products']
            for p1 in products:
                if p1 not in self.product_associations:
                    self.product_associations[p1] = Counter()
                for p2 in products:
                    if p1 != p2:
                        self.product_associations[p1][p2] += 1
    
    def get_recommendations(self, num_recommendations=5):
        # 模拟获取最近的购买历史
        recent_purchases = [item['item_id'] for item in self.data[-5:]]
        
        # 基于关联规则生成推荐
        recommendations = Counter()
        for product in recent_purchases:
            if product in self.product_associations:
                recommendations.update(self.product_associations[product])
        
        # 移除已购买的商品
        for product in recent_purchases:
            if product in recommendations:
                del recommendations[product]
        
        # 计算支持度和置信度
        total_transactions = len(self.data)
        recommended_items = []
        
        for product, count in recommendations.most_common(num_recommendations):
            support = count / total_transactions
            confidence = count / sum(self.product_associations[product].values())
            recommended_items.append({
                'product': product,
                'support': support,
                'confidence': confidence
            })
        
        # 计算准确率（这里使用模拟数据）
        accuracy = len(recommended_items) / num_recommendations if recommended_items else 0
        
        return {
            'items': recommended_items,
            'history': recent_purchases,
            'accuracy': accuracy
        } 