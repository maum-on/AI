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
        version="0.1.0"
    )

    # ------------------------------------
    # ⚙️ Middleware
    # ------------------------------------
    app.add_middleware(ApiKeyMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 배포 시 특정 도메인으로 제한 가능
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------
    # 🗂 기존 서비스 라우터
    # ------------------------------------
    app.include_router(diary.router, prefix="/diary")
    app.include_router(user.router,  prefix="/user")

    # ------------------------------------
    # ✨ Chat-to-Diary
    # (이미 라우터 내부에 prefix="/chat-diary" 있음)
    # ------------------------------------
    app.include_router(chat_diary_router)

    # ------------------------------------
    # ✨ Picture-Diary (이번에 만든 기능)
    # prefix는 picture_diary_router 내부에 이미 선언됨
    # ------------------------------------
    app.include_router(picture_diary_router)

    # ------------------------------------
    # 🩺 Health Check
    # ------------------------------------
    @app.get("/health")
    def health():
        return {"ok": True}

    return app


# ------------------------------------
# ⚡ FastAPI 실행 객체
# (배포/로컬 실행 모두 이 객체 사용)
# ------------------------------------
app = create_app()
