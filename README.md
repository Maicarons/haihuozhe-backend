# 海活者后端服务器

这是一个基于FastAPI的服务器，用于监控用户打卡超时情况并向钉钉发送推送通知。

## 功能

- 监控用户打卡超时
- 支持钉钉推送方式
- 自动定时检查超时用户
- RESTful API接口

## 部署到Vercel

此项目可以直接部署到Vercel平台，无需额外配置。

## API接口

### 创建用户
```bash
POST /users/
Content-Type: application/json

{
  "user_id": "user123",
  "timeout_duration": 24,
  "push_rules": [
    {
      "id": "rule1",
      "type": "dingtalk",
      "enabled": true,
      "config": {
        "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=your_dingtalk_robot_token",
        "secret": "your_dingtalk_robot_secret"
      }
    }
  ]
}
```

### 用户打卡
```bash
POST /users/{user_id}/checkin
```

### 获取用户信息
```bash
GET /users/{user_id}
```

### 获取用户超时配置
```bash
GET /users/{user_id}/timeout-config
```

## 支持的推送类型

1. **钉钉推送** - 通过钉钉机器人发送消息，当用户超过设定时间未打卡时，会发送"用户xxx已经xx时间没有打卡"的消息

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行本地服务器
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
uvicorn app:app --reload
```

## 部署

直接将此目录部署到Vercel即可。