import os
from pathlib import Path


def ensure_directory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_path(base_path: str, *parts: str) -> str:
    return os.path.join(base_path, *parts)


def delete_file(file_path: str) -> bool:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError:
        pass
    return False
