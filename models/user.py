from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .push_rule import PushRule


class CheckinUser(BaseModel):
    user_id: str
    timeout_duration: int  # 超时时间（小时）
    push_rules: List[PushRule]
    last_checkin_time: Optional[datetime] = None
    timezone: str = "Asia/Shanghai"