import os
import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# 로깅 기본 설정
logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

# .env에서 내부 인증용 API 키 로드
API_KEY = os.getenv("INTERNAL_API_KEY")

class RequestContextMiddleware(BaseHTTPMiddleware):
    """요청마다 고유 ID 부여 및 실행 시간 로깅"""
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())[:8]
        request.state.request_id = req_id
        t0 = time.time()
        response = await call_next(request)
        dt = int((time.time() - t0) * 1000)
        logger.info(f"[{req_id}] {request.method} {request.url.path} {response.status_code} {dt}ms")
        response.headers["X-Request-Id"] = req_id
        return response


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """내부 API 키 인증 미들웨어"""
    async def dispatch(self, request: Request, call_next):
        # /docs, /openapi, /health 는 무조건 허용
        if request.url.path.startswith(("/docs", "/openapi", "/health")):
            return await call_next(request)

        # .env에 INTERNAL_API_KEY가 지정되어 있으면 헤더 확인
        if API_KEY:
            header_key = request.headers.get("X-API-Key")
            if header_key != API_KEY:
                return JSONResponse({"detail": "Forbidden"}, status_code=403)

        return await call_next(request)
