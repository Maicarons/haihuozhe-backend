@echo off
REM 激活conda环境
call conda activate hhz-backend

REM 运行fastapi应用
uvicorn app:app --host 0.0.0.0 --port 8909
