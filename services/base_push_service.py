from abc import ABC, abstractmethod
from models.user import CheckinUser


class BasePushService(ABC):
    """推送服务基类"""
    
    @abstractmethod
    async def send_notification(self, config: dict, user: CheckinUser):
        """发送通知"""
        pass