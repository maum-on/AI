from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from .middleware import RequestContextMiddleware, ApiKeyMiddleware
from .routers import diary, user

# ⬇️ 새로 만든 chat-to-diary 라우터 import 추가
from src.routers.chat_to_diary import router as chat_diary_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Diary Replier",
        version="0.1.0"
    )

    # -------------------------
    # ⚙️ Middleware 등록
    # -------------------------
    app.add_middleware(ApiKeyMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],       # 배포 시 특정 도메인으로 제한 권장
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------
    # 🗂 기존 서비스 라우터
    # -------------------------
    app.include_router(diary.router, prefix="/diary")
    app.include_router(user.router,  prefix="/user")

    # -------------------------
    # ✨ 새 서비스: Chat-to-Diary 라우터
    # -------------------------
    # prefix="/chat-diary"는 router 내부에 이미 있음
    # (src/routers/chat_to_diary.py → APIRouter(prefix="/chat-diary"))
    app.include_router(chat_diary_router)

    # -------------------------
    # 🩺 Health Check
    # -------------------------
    @app.get("/health")
    def health():
        return {"ok": True}

    return app


# FastAPI 실행 객체
app = create_app()


