import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载 .env（开发环境）
load_dotenv()

# 初始化日志目录
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 初始化 FastAPI 应用
app = FastAPI(
    title="ColdAtom Simulator API",
    description="Secure cold atom simulation training service for research and education.",
    version="3.0"
)

# 挂载静态文件（提供 HTML 页面）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 从环境变量读取 Token（必须设置）
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("❌ Missing API_TOKEN in environment. Please set it in .env file.")

# Token 验证依赖
async def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {API_TOKEN}":
        logging.warning("Unauthorized access attempt with token: %s", authorization)
        raise HTTPException(status_code=401, detail="Invalid or missing API token")

# 请求模型
class TrainRequest(BaseModel):
    model_name: str
    timesteps: int

# 训练接口
@app.post("/train", summary="Submit a training job")
async def train_model(request: TrainRequest, token: str = Depends(verify_token)):
    from app.utils import is_valid_model_name, get_safe_model_path

    # 安全校验 1: timesteps 范围
    if not (100 <= request.timesteps <= 1_000_000):
        raise HTTPException(
            status_code=400,
            detail="timesteps must be an integer between 100 and 1,000,000"
        )

    # 安全校验 2: 模型文件名格式
    if not is_valid_model_name(request.model_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid model_name. Must match pattern: [a-zA-Z0-9_-]+.zip"
        )

    # 安全校验 3: 路径沙箱
    try:
        safe_path = get_safe_model_path(request.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 记录合法请求
    logging.info("Training requested: model=%s, timesteps=%d", request.model_name, request.timesteps)

    # TODO: 此处可调用你的 ColdAtom_Simulator_v3.0... 主程序
    # 例如：subprocess.run(["./ColdAtom_Simulator_v3.0...", "--model", str(safe_path), "--steps", str(request.timesteps)])

    return {
        "status": "accepted",
        "model_path": str(safe_path),
        "message": f"Training job for '{request.model_name}' queued with {request.timesteps} steps."
    }

# 健康检查
@app.get("/health", summary="Service health check")
async def health():
    return {"status": "ok", "service": "ColdAtom_Simulator", "version": "3.0"}