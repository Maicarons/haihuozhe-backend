from fastapi import APIRouter, HTTPException, Depends
from fastapi.requests import Request
from typing import List
from models.user import CheckinUser

# 创建用户路由
router = APIRouter(prefix="/users", tags=["users"])


def get_user_storage(request: Request):
    """从请求中获取用户存储实例"""
    return request.app.state.user_storage


def get_timeout_checker(request: Request):
    """从请求中获取超时检查器实例"""
    return request.app.state.timeout_checker


@router.get("/{user_id}")
async def get_user(user_id: str, user_storage=Depends(get_user_storage)):
    """获取用户信息"""
    user = user_storage.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    return user


@router.post("/")
async def create_user(user: CheckinUser, user_storage=Depends(get_user_storage)):
    """创建用户"""
    user_storage.save_user(user)
    return {"message": "用户创建成功", "user_id": user.user_id}


@router.put("/{user_id}")
async def update_user(user_id: str, user: CheckinUser, user_storage=Depends(get_user_storage)):
    """更新用户信息"""
    existing_user = user_storage.get_user(user_id)
    
    if not existing_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    # 保持原有的打卡时间
    user.last_checkin_time = existing_user.last_checkin_time
    
    user_storage.save_user(user)
    return {"message": "用户更新成功", "user_id": user.user_id}


@router.post("/{user_id}/checkin")
async def user_checkin(user_id: str, user_storage=Depends(get_user_storage)):
    """用户打卡"""
    user = user_storage.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    from datetime import datetime
    user.last_checkin_time = datetime.now()
    user_storage.save_user(user)
    
    return {"message": "打卡记录成功", "checkin_time": user.last_checkin_time}


@router.get("/{user_id}/timeout-config")
async def get_timeout_config(user_id: str, user_storage=Depends(get_user_storage)):
    """获取用户超时配置"""
    user = user_storage.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    return {
        "timeout_duration": user.timeout_duration,
        "last_checkin_time": user.last_checkin_time,
        "push_rules": user.push_rules
    }
