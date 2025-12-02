import ollama
import logging
import uvicorn

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from routes import api_router

# global variables
API_PORT = 6000
model_available = False
AVAILABLE_MODELS = []

# Log config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_available, AVAILABLE_MODELS
    logger.info(f"Starting API server on port {API_PORT}")
    
    try:
        models_response = ollama.list()
        model_available = True
        AVAILABLE_MODELS = [m.get("name", "").split(":")[0] for m in models_response.get("models", [])]
        logger.info("Connected to ollama service")
        logger.info(f"Available models: {', '.join(AVAILABLE_MODELS)}")
    except Exception as e:
        logger.error(f"Failed to connect to Ollama service: {e}")
        model_available = False
    
    yield
    
    logger.info("API server closed")

app = FastAPI(
    title="Local Models API",
    version="1.0.0",
    description="RESTful API",
    lifespan=lifespan,
    docs_url=None,    # 禁用預設 docs
    redoc_url=None,   # 禁用預設 redoc
)

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# security
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # 記錄 request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # 記錄 response
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """健康檢查：返回 Ollama 連接狀態和可用模型"""
    try:
        return {
            "status": "healthy" if model_available else "unhealthy",
            "ollama_connected": model_available,
            "available_models": AVAILABLE_MODELS,
            "models_count": len(AVAILABLE_MODELS)
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# routes
app.include_router(api_router, prefix="/api/v1")

# custom 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.warning(f"404 Not Found: {request.url.path}")
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"路徑 {request.url.path} 不存在",
            "status_code": 404
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=API_PORT, reload=True)