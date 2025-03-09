# -*- coding: utf-8 -*-

class DataProcessor:
    def __init__(self):
        self.rules = []
        self.purchase_history = []
        self._init_sample_data()

    def _init_sample_data(self):
        """初始化示例数据"""
        # 示例购买历史
        self.purchase_history = [
            {'user_id': 1, 'items': ['手机', '耳机']},
            {'user_id': 1, 'items': ['充电器', '手机壳']},
            {'user_id': 2, 'items': ['平板', '触控笔']},
            # ... 更多历史数据
        ]

        # 示例关联规则
        self.rules = [
            {
                'antecedent': ['手机', '耳机'],
                'consequent': '充电器',
                'confidence': 0.9,
                'support': 0.3
            },
            {
                'antecedent': ['平板'],
                'consequent': '触控笔',
                'confidence': 0.8,
                'support': 0.25
            },
            # ... 更多规则
        ]

    def get_user_history(self, user_id):
        """获取用户购买历史"""
        return [
            item for purchase in self.purchase_history 
            if purchase['user_id'] == user_id 
            for item in purchase['items']
        ]

    def get_recommendations(self, user_id, max_items=5):
        """生成推荐"""
        user_history = self.get_user_history(user_id)
        recommendations = []
        
        for rule in self.rules:
            if set(rule['antecedent']).issubset(set(user_history)):
                if rule['consequent'] not in user_history:
                    recommendations.append({
                        'product': rule['consequent'],
                        'confidence': rule['confidence'],
                        'support': rule['support']
                    })

        return recommendations[:max_items] 