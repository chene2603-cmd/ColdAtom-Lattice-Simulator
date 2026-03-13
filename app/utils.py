import re
from pathlib import Path

def is_valid_model_name(name: str) -> bool:
    """
    校验模型文件名是否合法。
    允许字母、数字、下划线、连字符，且必须以 .zip 结尾。
    """
    return re.fullmatch(r'[a-zA-Z0-9_-]+\.zip', name) is not None

def get_safe_model_path(name: str) -> Path:
    """
    返回安全的模型保存路径，防止路径遍历或符号链接攻击。
    确保最终路径严格位于 ./models/ 目录内。
    """
    base_dir = Path("models").resolve()
    target = (base_dir / name).resolve()

    # 检查是否仍在 base_dir 内（防御 ../ 或符号链接）
    if not str(target).startswith(str(base_dir)):
        raise ValueError("Path traversal detected: invalid model path")

    # 自动创建 models 目录
    base_dir.mkdir(exist_ok=True)
    return target