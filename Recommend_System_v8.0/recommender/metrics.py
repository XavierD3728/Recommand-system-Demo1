# -*- coding: utf-8 -*-
import time
from datetime import datetime

class MetricsTracker:
    def __init__(self):
        self.start_time = None
        self.history = []

    def start(self):
        """开始计时"""
        self.start_time = time.time()

    def record_metrics(self, recommendations, actual_items):
        """记录性能指标"""
        if not self.start_time:
            return {
                'accuracy': 0,
                'processing_time': 0
            }

        processing_time = time.time() - self.start_time
        
        # 计算准确率
        if not recommendations or not actual_items:
            accuracy = 0.0
        else:
            recommended_set = set(r['product'] for r in recommendations)
            actual_set = set(actual_items)
            hits = len(recommended_set.intersection(actual_set))
            accuracy = hits / len(recommendations)

        metrics = {
            'accuracy': accuracy,
            'processing_time': processing_time
        }
        self.history.append(metrics)
        return metrics

    def get_average_metrics(self):
        """获取平均指标"""
        if not self.history:
            return {
                'avg_accuracy': 0.0,
                'avg_processing_time': 0.0
            }

        total = len(self.history)
        return {
            'avg_accuracy': sum(m['accuracy'] for m in self.history) / total,
            'avg_processing_time': sum(m['processing_time'] for m in self.history) / total
        } 