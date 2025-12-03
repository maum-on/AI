from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# 🧱 Middleware
# -------------------------
from .middleware import RequestContextMiddleware, ApiKeyMiddleware

# -------------------------
# 📚 기존 라우터
# -------------------------
from .routers import diary, user

# -------------------------
# ✨ 새로운 라우터들
# -------------------------
from api.routers.picture_diary_router import router as picture_diary_router
from src.routers.chat_to_diary import router as chat_diary_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Diary Replier + 그림일기 DEV",
        version="0.1.0",
    )

    # ------------------------------------
    # ⚙️ CORS 설정
    # ------------------------------------
    origins = [
        "http://54.79.20.218:8000",
        "http://13.209.35.235:8080",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------
    # ⚙️ 기타 미들웨어
    # ------------------------------------
    app.add_middleware(ApiKeyMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # ------------------------------------
    # 🗂 기존 서비스 라우터
    # ------------------------------------
    app.include_router(diary.router, prefix="/diary")
    app.include_router(user.router, prefix="/user")

    # ------------------------------------
    # ✨ Chat-to-Diary
    # ------------------------------------
    app.include_router(chat_diary_router)

    # ------------------------------------
    # ✨ Picture-Diary
    # ------------------------------------
    app.include_router(picture_diary_router)

    # ------------------------------------
    # 🩺 Health Check
    # ------------------------------------
    @app.get("/health")
    def health():
        return {"ok": True}

    return app


app = create_app()
