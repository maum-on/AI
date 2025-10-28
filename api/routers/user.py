from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.models import UserPreset, get_session

router = APIRouter(prefix="/user", tags=["user"])

class PresetIn(BaseModel):
    user_id: str
    preset: str  # warm | coach | short
    mood_default: str | None = None

@router.post("/preset")
def set_preset(body: PresetIn, db: Session = Depends(get_session)):
    up = db.query(UserPreset).filter_by(user_id=body.user_id).first()
    if not up:
        up = UserPreset(
            user_id=body.user_id,
            preset=body.preset,
            mood_default=body.mood_default
        )
        db.add(up)
    else:
        up.preset = body.preset
        up.mood_default = body.mood_default
    db.commit()
    return {"ok": True, "user_id": body.user_id, "preset": body.preset}

@router.get("/preset/{user_id}")
def get_preset(user_id: str, db: Session = Depends(get_session)):
    up = db.query(UserPreset).filter_by(user_id=user_id).first()
    if not up:
        raise HTTPException(status_code=404, detail="Preset not found")
    return {
        "user_id": user_id,
        "preset": up.preset,
        "mood_default": up.mood_default
    }
