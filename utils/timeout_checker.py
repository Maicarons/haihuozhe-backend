import logging
from datetime import datetime
from typing import Dict
from models.user import CheckinUser
from services.push_service_manager import PushServiceManager


logger = logging.getLogger(__name__)


class TimeoutChecker:
    """超时检查器"""
    
    def __init__(self):
        self.service_manager = PushServiceManager()
    
    async def check_user_timeout(self, user: CheckinUser) -> bool:
        """检查单个用户是否超时"""
        if not user.last_checkin_time:
            return False  # 如果从未打卡过，不认为是超时
        
        current_time = datetime.now()
        time_diff = current_time - user.last_checkin_time
        
        # 检查是否超过超时时间（单位：小时）
        return time_diff.total_seconds() > user.timeout_duration * 3600
    
    async def trigger_push_notifications(self, user: CheckinUser):
        """触发推送通知，只处理钉钉推送"""
        logger.info(f"为用户 {user.user_id} 触发推送通知")
        
        for rule in user.push_rules:
            if not rule.enabled or rule.type != "dingtalk":
                continue
            
            try:
                service = self.service_manager.get_service(rule.type)
                await service.send_notification(rule.config, user)
                logger.info(f"成功发送 {rule.type} 通知给用户 {user.user_id}")
            except Exception as e:
                logger.error(f"发送 {rule.type} 通知失败，用户 {user.user_id}: {str(e)}")
    
    async def check_all_users_timeout(self, users_db: Dict[str, CheckinUser]):
        """检查所有用户是否超时"""
        logger.info("正在检查超时用户...")
        
        for user_id, user in users_db.items():
            is_timed_out = await self.check_user_timeout(user)
            
            if is_timed_out:
                logger.info(f"用户 {user_id} 已超时，触发推送通知...")
                await self.trigger_push_notifications(user)