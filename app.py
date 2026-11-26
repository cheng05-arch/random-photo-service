"""实验1：随机图片 HTTP 服务。

接口：GET /photo 随机返回 images/ 目录内的一张图片。
异常：目录不存在、没有图片或目录无法读取时，返回 HTTP 503 和 JSON 说明。
"""

from pathlib import Path
import mimetypes
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

app = FastAPI(title="随机图片 HTTP 服务", version="1.0.0")


def list_images() -> list[Path]:
    """每次请求时读取图片目录，便于后续直接添加新照片。"""
    try:
        return [
            item
            for item in IMAGE_DIR.iterdir()
            if item.is_file() and item.suffix.lower() in ALLOWED_SUFFIXES
        ]
    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError):
        return []


@app.get("/", include_in_schema=False)
def index():
    """实验首页提供三个常用接口入口。"""
    return FileResponse(BASE_DIR / "index.html", media_type="text/html")


@app.get("/health")
def health():
    """返回当前可用图片数量。"""
    return {"status": "ok", "image_count": len(list_images())}


@app.get("/photo", responses={503: {"description": "图片目录为空或不可用"}})
def get_random_photo():
    """从服务器指定目录随机选择一张图片并返回其二进制内容。"""
    candidates = list_images()
    if not candidates:
        raise HTTPException(
            status_code=503,
            detail="No images available: please add JPG/PNG/GIF/WebP files to images/",
        )

    selected = secrets.choice(candidates)
    media_type = mimetypes.guess_type(selected.name)[0] or "application/octet-stream"
    return FileResponse(
        path=selected,
        media_type=media_type,
        headers={
            "Cache-Control": "no-store",
            "X-Image-Name": selected.name,
        },
    )
