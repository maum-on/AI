from fastapi import Header
from sqlalchemy.orm import Session
from api.models import get_session

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

class UserCtx:
    def __init__(self, user_id: str | None, preset_override: str | None):
        self.user_id = user_id
        self.preset_override = preset_override

async def get_user_ctx(
    x_user_id: str | None = Header(default=None, convert_underscores=False),
    x_preset: str | None = Header(default=None, convert_underscores=False),
):
    # 헤더 예: X-User-Id, X-Preset
    return UserCtx(user_id=x_user_id, preset_override=x_preset)
