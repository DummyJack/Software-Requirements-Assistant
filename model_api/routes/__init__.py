from fastapi import APIRouter
from .model import router as model_router

# 統一管理所有路由
api_router = APIRouter()

# 模型
api_router.include_router(model_router, tags=["model"])

