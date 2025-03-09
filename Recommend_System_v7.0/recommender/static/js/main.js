// 使用立即执行函数避免全局变量污染
(function() {
    // 状态变量
    let isLoading = false;
    let currentUserId = 1;

    // DOM 加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        console.log('页面初始化...');
        
        // 绑定按钮点击事件
        document.getElementById('getRecommendationsBtn').addEventListener('click', function() {
            getRecommendations(currentUserId);
        });
        
        // 绑定用户选择事件
        document.getElementById('userSelector').addEventListener('change', function() {
            currentUserId = parseInt(this.value);
            getRecommendations(currentUserId);
        });
        
        // 初始化加载
        loadCategories();
        getRecommendations(currentUserId);
    });

    // 设置加载状态
    function setLoading(state) {
        isLoading = state;
        const button = document.getElementById('getRecommendationsBtn');
        button.disabled = state;
        button.textContent = state ? '加载中...' : '获取推荐';
    }

    // 显示消息
    function showMessage(elementId, message, isError = false) {
        const element = document.getElementById(elementId);
        const className = isError ? 'error' : '';
        element.innerHTML = `<div class="${className}">${message}</div>`;
    }

    // 显示加载中
    function showLoading(elementId) {
        const element = document.getElementById(elementId);
        element.innerHTML = '<div class="loading">加载中...</div>';
    }

    // 安全地处理HTML内容，防止XSS攻击
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // 更新性能指标
    function updateMetrics(metrics) {
        if (metrics) {
            document.getElementById('recommendationAccuracy').textContent = `${(metrics.accuracy * 100).toFixed(2)}%`;
            document.getElementById('recommendationTime').textContent = `${metrics.processing_time_ms.toFixed(2)}毫秒`;
            document.getElementById('matchedRules').textContent = metrics.matched_rules;
            document.getElementById('totalRules').textContent = metrics.total_rules;
        } else {
            document.getElementById('recommendationAccuracy').textContent = '-';
            document.getElementById('recommendationTime').textContent = '-';
            document.getElementById('matchedRules').textContent = '-';
            document.getElementById('totalRules').textContent = '-';
        }
    }

    // 加载商品类别
    function loadCategories() {
        showLoading('categories');
        
        fetch('/get_categories')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.success && data.categories) {
                    let html = '';
                    try {
                        for (const category in data.categories) {
                            if (data.categories.hasOwnProperty(category)) {
                                const products = data.categories[category];
                                html += `
                                    <div class="category-group">
                                        <div class="category-title">${escapeHtml(category)}</div>
                                        <div class="category-items">`;
                                
                                products.forEach(product => {
                                    html += `<div class="product-item">${escapeHtml(product)}</div>`;
                                });
                                
                                html += `
                                        </div>
                                    </div>`;
                            }
                        }
                        document.getElementById('categories').innerHTML = html || '<div>暂无商品类别</div>';
                    } catch (e) {
                        console.error('处理类别数据出错:', e);
                        showMessage('categories', '处理数据时出错', true);
                    }
                } else {
                    showMessage('categories', '暂无商品类别');
                }
            })
            .catch(error => {
                console.error('加载类别失败:', error);
                showMessage('categories', '加载失败，请刷新重试', true);
            });
    }

    // 获取推荐
    function getRecommendations(userId) {
        if (isLoading) return;
        
        setLoading(true);
        showLoading('purchaseHistory');
        showLoading('recommendedProducts');
        updateMetrics(null);

        fetch('/get_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('推荐数据:', data); // 调试日志
            
            try {
                if (data && data.success) {
                    // 更新历史购买记录
                    let historyHtml = '';
                    if (data.historical_purchases && data.historical_purchases.length > 0) {
                        historyHtml += `<div class="recommendation-header">
                            <h3>用户 ${userId} 的购买记录</h3>
                            <span class="recommendation-count">${data.historical_purchases.length} 件商品</span>
                        </div>`;
                        
                        data.historical_purchases.forEach(item => {
                            historyHtml += `<div class="product-item">${escapeHtml(item)}</div>`;
                        });
                    }
                    document.getElementById('purchaseHistory').innerHTML = historyHtml || '<div>暂无历史购买记录</div>';

                    // 更新推荐商品
                    let recsHtml = '';
                    if (data.recommendations && data.recommendations.length > 0) {
                        recsHtml += `<div class="recommendation-header">
                            <h3>为用户 ${userId} 的推荐</h3>
                            <span class="recommendation-count">${data.recommendations.length} 件商品</span>
                        </div>`;
                        
                        data.recommendations.forEach(item => {
                            if (item && typeof item === 'object' && item.product) {
                                recsHtml += `
                                    <div class="product-item">
                                        ${escapeHtml(item.product)} (${escapeHtml(item.category || '未分类')})
                                        <br>
                                        <small>
                                            置信度: ${(item.confidence * 100).toFixed(2)}%,
                                            支持度: ${(item.support * 100).toFixed(2)}%
                                        </small>
                                    </div>`;
                            }
                        });
                    }
                    document.getElementById('recommendedProducts').innerHTML = recsHtml || '<div>暂无推荐商品</div>';

                    // 更新性能指标
                    updateMetrics(data.metrics);
                } else {
                    throw new Error(data.error || '获取数据失败');
                }
            } catch (e) {
                console.error('处理推荐数据出错:', e);
                showMessage('purchaseHistory', '处理数据时出错', true);
                showMessage('recommendedProducts', '处理数据时出错', true);
                updateMetrics(null);
            }
        })
        .catch(error => {
            console.error('获取推荐失败:', error);
            showMessage('purchaseHistory', '获取数据失败', true);
            showMessage('recommendedProducts', '获取数据失败', true);
            updateMetrics(null);
        })
        .finally(() => {
            setLoading(false);
        });
    }
})(); 