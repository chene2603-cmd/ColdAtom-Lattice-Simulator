from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import os
from pathlib import Path
from app import auth, train, utils

app = FastAPI()

# === 安全措施 1：API Token 认证 ===
# 从环境变量读取 Token（不要硬编码！）
API_TOKEN = os.getenv("API_TOKEN", "your-secret-token")

async def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")

# === 安全措施 2：限制 timesteps 范围 ===
class TrainRequest(BaseModel):
    model_name: str
    timesteps: int

@app.post("/train")
async def train_model(
    request: TrainRequest,
    token: str = Depends(verify_token)
):
    # 1. 校验 timesteps 范围（防止恶意超长训练）
    if not (100 <= request.timesteps <= 1_000_000):
        raise HTTPException(status_code=400, detail="timesteps must be between 100 and 1,000,000")

    # 2. 过滤模型文件名（防止路径遍历）
    if not utils.is_valid_model_name(request.model_name):
        raise HTTPException(status_code=400, detail="Invalid model name")

    # 3. 安全路径处理（防止符号链接攻击）
    model_path = utils.get_safe_model_path(request.model_name)

    # 4. 执行训练
    result = train.run_training(model_path, request.timesteps)

    return {"status": "success", "model_path": model_path, "result": result}

# === 健康检查 ===
@app.get("/health")
async def health():
    return {"status": "ok"}