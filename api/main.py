from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .middleware import RequestContextMiddleware, ApiKeyMiddleware
from .routers import diary, user

def create_app() -> FastAPI:
    app = FastAPI(title="Diary Replier", version="0.1.0")

    # 미들웨어 등록
    app.add_middleware(ApiKeyMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],            # 배포 시 도메인으로 제한 권장
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(diary.router)
    app.include_router(user.router)

    # 헬스체크
    @app.get("/health")
    def health():
        return {"ok": True}

    return app

app = create_app()
