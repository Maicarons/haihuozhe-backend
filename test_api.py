import pytest
import asyncio
from httpx import AsyncClient
from app import app


@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_and_get_user():
    # 创建用户
    user_data = {
        "user_id": "test_user_123",
        "timeout_duration": 24,
        "push_rules": [
            {
                "id": "rule1",
                "type": "dingtalk",
                "enabled": True,
                "config": {
                    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=test_token",
                    "secret": "test_secret"
                }
            }
        ]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 创建用户
        response = await ac.post("/users/", json=user_data)
        assert response.status_code == 200
        
        # 获取用户
        response = await ac.get("/users/test_user_123")
        assert response.status_code == 200
        assert response.json()["user_id"] == "test_user_123"


@pytest.mark.asyncio
async def test_user_checkin():
    # 首先创建用户
    user_data = {
        "user_id": "checkin_test_user",
        "timeout_duration": 24,
        "push_rules": [
            {
                "id": "rule1",
                "type": "dingtalk",
                "enabled": True,
                "config": {
                    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=test_token",
                    "secret": "test_secret"
                }
            }
        ]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 创建用户
        response = await ac.post("/users/", json=user_data)
        assert response.status_code == 200
        
        # 用户打卡
        response = await ac.post("/users/checkin_test_user/checkin")
        assert response.status_code == 200
        assert "checkin_time" in response.json()


if __name__ == "__main__":
    pytest.main(["-v"])