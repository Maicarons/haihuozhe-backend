from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.responses import FileResponse
from db.user_storage import UserStorage
from utils.timeout_checker import TimeoutChecker
from routes import users_router


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期管理器"""
    logger.info("正在启动...")
    
    # 初始化用户存储
    user_storage = UserStorage()
    app.state.user_storage = user_storage
    
    # 初始化超时检查器
    timeout_checker = TimeoutChecker()
    app.state.timeout_checker = timeout_checker
    
    # 启动定时任务调度器
    scheduler = AsyncIOScheduler()
    scheduler.start()
    
    # 每分钟检查一次打卡超时
    scheduler.add_job(
        check_all_users_timeout_job, 
        "interval", 
        minutes=1,
        args=[app]
    )
    
    app.state.scheduler = scheduler
    
    yield
    
    # 关闭调度器
    scheduler.shutdown()


async def check_all_users_timeout_job(app: FastAPI):
    """检查所有用户超时的作业函数"""
    timeout_checker = app.state.timeout_checker
    user_storage = app.state.user_storage
    users_db = user_storage.get_all_users()
    
    await timeout_checker.check_all_users_timeout(users_db)


app = FastAPI(lifespan=lifespan)

# 注册路由
app.include_router(users_router)


@app.get("/")
async def read_root():
    """根路径"""
    return {"message": "FastAPI server for check-in timeout monitoring", "version": "1.0.0"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """网站图标"""
    return FileResponse("logo.png")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "service": "check-in timeout monitoring"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
