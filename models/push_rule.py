from pydantic import BaseModel
from typing import Dict


class PushRule(BaseModel):
    id: str
    type: str  # 'dingtalk'
    enabled: bool = True
    config: Dict[str, str]  # 推送配置