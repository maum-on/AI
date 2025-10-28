# api/deps.py
from functools import lru_cache
from typing import Callable, Optional, Dict, Any
import os
import yaml

from dotenv import load_dotenv

# 1) 앱 시작 시 .env 로드 (한 번만)
load_dotenv()

# 2) 설정 객체
class Settings:
    def __init__(self):
        # 환경변수
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.model_name: str = os.getenv("DIARY_MODEL_NAME", "gpt-4o-mini")
        self.config_path: str = os.getenv("CONFIG_PATH", "config.yaml")

        # config.yaml (선택) 로드
        self.cfg: Dict[str, Any] = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.cfg = yaml.safe_load(f) or {}

        # cfg 우선순위로 병합
        self.model_name = self.cfg.get("model_name", self.model_name)

@lru_cache
def get_settings() -> Settings:
    # FastAPI에서 Depends(get_settings)로 주입 시 싱글톤처럼 동작
    return Settings()

# 3) 파이프라인 주입: settings를 캡처한 callable 반환
def get_pipeline() -> Callable:
    settings = get_settings()   # ✅ 내부에서 꺼내기
    from diary_replier.pipeline import diary_to_reply
    def _pipeline(payload):
        return diary_to_reply(payload, settings=settings)
    return _pipeline
