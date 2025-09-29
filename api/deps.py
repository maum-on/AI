# api/deps.py
import os, yaml

class Settings:
    def __init__(self):
        path = os.getenv("RUNTIME_CONFIG", "configs/runtime.yaml")
        cfg = {}
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        cfg = data
        except Exception:
            pass
        self.cfg = cfg

def get_settings():
    return Settings()

def get_pipeline():
    # 지연 import로 순환참조/테스트 시 문제 방지
    from diary_replier.pipeline import diary_to_reply
    return diary_to_reply

