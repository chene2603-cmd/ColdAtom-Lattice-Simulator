import time
import logging
from pathlib import Path

def run_training(model_path: Path, timesteps: int):
    logging.info(f"Starting training: {model_path}, timesteps={timesteps}")
    # 模拟训练过程
    time.sleep(2)
    return f"Trained {timesteps} steps, saved to {model_path}"