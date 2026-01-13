import logging
import hmac
import hashlib
import base64
import urllib.parse
import aiohttp
from services.base_push_service import BasePushService
from models.user import CheckinUser
from datetime import datetime


logger = logging.getLogger(__name__)


class DingtalkService(BasePushService):
    """钉钉推送服务"""
    
    async def send_notification(self, config: dict, user: CheckinUser):
        """发送钉钉通知"""
        webhook_url = config.get("webhook_url")
        secret = config.get("secret", "")
        
        if not webhook_url:
            raise ValueError("缺少必要的钉钉配置")
        
        # 构建消息内容
        message = f"用户 {user.user_id} 已超过 {user.timeout_duration} 小时未打卡。\n最后打卡时间: {user.last_checkin_time}\n当前时间: {datetime.now()}"
        
        # 如果有安全密钥，需要计算签名
        timestamp = str(round(datetime.now().timestamp() * 1000))
        sign = ""
        
        if secret:
            secret_enc = secret.encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, secret)
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        # 构建最终的webhook URL
        final_webhook = webhook_url
        if secret:
            final_webhook = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        
        payload = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(final_webhook, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"钉钉API返回状态 {response.status}")
                    result = await response.json()
                    if result.get("errcode") != 0:
                        raise Exception(f"钉钉API错误: {result}")
                    logger.info("钉钉通知已发送")
        except Exception as e:
            logger.error(f"发送钉钉通知失败: {str(e)}")
            raise