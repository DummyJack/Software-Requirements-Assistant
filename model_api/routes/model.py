from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import ollama
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Request model
class CompletionRequest(BaseModel):
    prompt: str = Field(..., description="提示詞")
    model: Optional[str] = Field(default="mistral", description="模型名稱")
    temperature: Optional[float] = Field(default=1, description="溫度(範圍: 0.0 ~ 2.0)")
    max_tokens: Optional[int] = Field(default=None)

# Response model
class CompletionResponse(BaseModel):
    response: str
    model: str
    created_at: str # 回應生成的時間戳記
    done: bool # 是否完成生成

@router.post("/completion", response_model=CompletionResponse, summary="生成")
async def create_completion(request: CompletionRequest):
    try:        
        options = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        
        # Ollama API
        response = ollama.generate(
            model=request.model,
            prompt=request.prompt,
            options=options if options else None
        )
        
        logger.info(f"({response['done']}){response['model']}: {response['response']}")
        
        return CompletionResponse(
            response=response["response"],
            model=response["model"],
            created_at=response["created_at"],
            done=response["done"]
        )
        
    except Exception as e:
        logger.error(f"Generate failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成失敗: {str(e)}"
        )
