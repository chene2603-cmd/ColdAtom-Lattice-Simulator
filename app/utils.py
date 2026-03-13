from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import logging
from pathlib import Path

# 初始化日志
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 加载环境变量（开发时用 .env，生产用系统环境变量）
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="ColdAtom Simulator API")

# 挂载静态文件目录（提供 HTML 页面）
app.mount("/static", StaticFiles(directory="static"), name="static")

# === 安全措施 1：Token 认证 ===
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN must be set in environment")

async def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid or missing token")

# === 安全措施 2：参数校验 ===
class TrainRequest(BaseModel):
    model_name: str
    timesteps: int

@app.post("/train")
async def train_model(
    request: TrainRequest,
    token: str = Depends(verify_token)
):
    from app.utils import is_valid_model_name, get_safe_model_path

    # 限制 timesteps 范围
    if not (100 <= request.timesteps <= 1_000_000):
        raise HTTPException(status_code=400, detail="timesteps must be between 100 and 1,000,000")

    # 过滤模型文件名
    if not is_valid_model_name(request.model_name):
        raise HTTPException(status_code=400, detail="Invalid model name. Must match [a-zA-Z0-9_-]+.zip")

    # 安全路径处理
    try:
        model_path = get_safe_model_path(request.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 模拟调用你的主程序（实际可替换为 subprocess）
    logging.info(f"Training started: {model_path}, timesteps={request.timesteps}")
    
    return {
        "status": "accepted",
        "message": f"Training {request.model_name} for {request.timesteps} steps."
    }

# === 健康检查 ===
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ColdAtom_Simulator"}