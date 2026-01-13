# 如何添加新的推送规则

本指南介绍如何为系统添加新的推送规则类型。

## 步骤

### 1. 创建新的推送服务类

在 `services` 目录下创建一个新的服务文件，例如 `pushbullet_service.py`：

```python
import logging
import aiohttp
from .base_push_service import BasePushService
from ..models.user import CheckinUser
from datetime import datetime


logger = logging.getLogger(__name__)


class PushbulletService(BasePushService):
    """Pushbullet推送服务"""
    
    async def send_notification(self, config: dict, user: CheckinUser):
        """发送Pushbullet通知"""
        api_token = config.get("api_token")
        device_iden = config.get("device_iden")
        
        if not api_token or not device_iden:
            raise ValueError("缺少必要的Pushbullet配置")
        
        message = f"用户 {user.user_id} 已超过 {user.timeout_duration} 小时未打卡。"
        
        payload = {
            "type": "note",
            "title": f"打卡超时提醒 - {user.user_id}",
            "body": message
        }
        
        headers = {
            "Access-Token": api_token,
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.pushbullet.com/v2/pushes",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Pushbullet API返回状态 {response.status}")
                    logger.info("Pushbullet通知已发送")
        except Exception as e:
            logger.error(f"发送Pushbullet通知失败: {str(e)}")
            raise
```

### 2. 更新服务管理器

在 `services/push_service_manager.py` 中导入新的服务类并在 `_register_default_services` 方法中注册：

```python
from .pushbullet_service import PushbulletService

# 在 _register_default_services 方法中添加:
self.register_service("pushbullet", PushbulletService)
```

### 3. 验证

启动服务器并测试新的推送规则类型。

## 设计原则

- 所有推送服务必须继承自 `BasePushService`
- 必须实现 `send_notification` 方法
- 使用适当的错误处理和日志记录
- 配置参数通过 `config` 字典传入
- 遵循单一职责原则，每个服务只负责一种推送方式

## 优点

这种架构提供了以下优势：

1. **易于扩展**: 添加新的推送服务只需要创建一个新类并注册
2. **松耦合**: 每个服务独立，不影响其他服务
3. **易维护**: 代码结构清晰，职责分离
4. **可测试**: 每个服务可以单独测试