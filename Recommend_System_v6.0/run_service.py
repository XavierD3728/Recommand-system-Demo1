import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    filename='recommendation_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RecommendationService')

class RecommendationService(win32serviceutil.ServiceFramework):
    _svc_name_ = "RecommendationSystem"
    _svc_display_name_ = "Recommendation System Service"
    _svc_description_ = "基于关联规则的商品推荐系统服务"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        """
        服务停止时调用
        """
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_alive = False
        logger.info('Service is stopping...')

    def SvcDoRun(self):
        """
        服务运行时调用
        """
        try:
            logger.info('Service is starting...')
            from run import app
            
            # 设置服务运行参数
            host = '0.0.0.0'  # 允许外部访问
            port = 5000       # 默认端口
            
            logger.info(f'Starting Flask app on {host}:{port}')
            app.run(host=host, port=port)
            
        except Exception as e:
            logger.error(f'Service error: {str(e)}')
            servicemanager.LogErrorMsg(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(RecommendationService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(RecommendationService) 