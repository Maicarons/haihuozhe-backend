from typing import Dict, Type
from services.base_push_service import BasePushService
from services.dingtalk_service import DingtalkService


class PushServiceManager:
    """推送服务管理器"""
    
    def __init__(self):
        self.services: Dict[str, Type[BasePushService]] = {}
        self._register_default_services()
    
    def _register_default_services(self):
        """注册默认推送服务"""
        self.register_service("dingtalk", DingtalkService)
    
    def register_service(self, service_type: str, service_class: Type[BasePushService]):
        """注册推送服务"""
        self.services[service_type] = service_class
    
    def get_service(self, service_type: str) -> BasePushService:
        """获取推送服务实例"""
        if service_type not in self.services:
            raise ValueError(f"未知的推送服务类型: {service_type}")
        
        return self.services[service_type]()