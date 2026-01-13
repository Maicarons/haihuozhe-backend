from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from datetime import datetime
from fastapi.responses import FileResponse
import os


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期管理器 - 适用于Vercel部署"""
    logger.info("正在启动Vercel应用...")
    
    # 在Vercel环境中，强制使用内存数据库，因为文件系统是只读的
    if os.environ.get("VERCEL"):
        os.environ.setdefault("USE_MEMORY_DB", "true")
    
    # 动态导入以避免循环依赖和路径问题
    from db.user_storage import UserStorage
    from utils.timeout_checker import TimeoutChecker
    
    # 初始化用户存储
    user_storage = UserStorage()
    app.state.user_storage = user_storage
    
    # 初始化超时检查器
    timeout_checker = TimeoutChecker()
    app.state.timeout_checker = timeout_checker
    
    # 注意：Vercel Serverless Functions 是无状态的
    # 长时间运行的后台任务（如APScheduler）在此环境中不可靠
    # 如果需要定期执行任务，请使用Vercel Cron Jobs或外部服务
    
    logger.info("Vercel应用启动完成")
    yield
    
    # 清理资源
    logger.info("正在关闭Vercel应用...")


app = FastAPI(lifespan=lifespan)

# 动态导入路由
from routes import users_router
# 注册路由
app.include_router(users_router)


@app.get("/")
async def read_root():
    """根路径"""
    return {"message": "FastAPI server for check-in timeout monitoring on Vercel", "version": "1.0.0"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """网站图标"""
    return FileResponse("../logo.png")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now(),
        "service": "check-in timeout monitoring on Vercel"
    }


# 添加一个端点用于手动触发超时检查（替代后台任务）
@app.post("/trigger-timeout-check")
async def trigger_timeout_check():
    """手动触发超时检查"""
    timeout_checker = app.state.timeout_checker
    user_storage = app.state.user_storage
    users_db = user_storage.get_all_users()
    
    await timeout_checker.check_all_users_timeout(users_db)
    return {"message": "Timeout check completed", "timestamp": datetime.now()}


# 根路径重定向到 docs
@app.get("/api")
async def api_docs_redirect():
    """API文档重定向"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")