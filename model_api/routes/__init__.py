from fastapi import APIRouter
from .model import router as model_router

# 統一管理所有路由
model_api_router = APIRouter()

# 模型路由
model_api_router.include_router(model_router, tags=["model"])

