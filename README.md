# 海活者后端服务器

这是一个基于FastAPI的服务器，用于监控用户打卡超时情况并向钉钉发送推送通知。此项目已针对Vercel部署进行了优化。

## 功能

- 监控用户打卡超时
- 支持钉钉推送方式
- RESTful API接口
- 优化的Vercel部署配置

## Vercel部署

此项目已配置为可在Vercel平台上一键部署，零配置需求。

### 部署步骤

1. 将此仓库连接到Vercel
2. Vercel将自动检测FastAPI应用程序
3. 使用`vercel.json`中的配置进行构建

或者使用Vercel CLI手动部署：

```bash
npm i -g vercel
vercel
```

### Vercel注意事项

- 应用程序配置为在Vercel Serverless Functions上运行
- 长时间运行的后台任务（如APScheduler）在Vercel环境中不可靠，因此已被禁用
- 使用`/trigger-timeout-check`端点手动触发超时检查
- 如需定期执行任务，请考虑使用Vercel Cron Jobs

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

### 手动触发超时检查
```bash
POST /trigger-timeout-check
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
uvicorn api.app:app --reload
```

## 部署

直接将此目录部署到Vercel即可。项目包含必要的配置文件以确保在Vercel上正常运行。