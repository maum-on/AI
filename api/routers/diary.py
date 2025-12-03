from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from diary_replier.schemas import DiaryInput, DiaryReplyOutput
from diary_replier.pipeline import run_pipeline_with_logging
from api.routers.deps import get_db, get_user_ctx, UserCtx
from api.models import DiaryLog

router = APIRouter(
    prefix="/diary",
    tags=["diary"],
)


@router.post("/reply", response_model=DiaryReplyOutput)
def make_reply(
    body: DiaryInput,
    db: Session = Depends(get_db),
    user_ctx: UserCtx = Depends(get_user_ctx),
):
    return run_pipeline_with_logging(
        body,
        user_id=user_ctx.user_id,
        preset_override=user_ctx.preset_override,
        db=db,
    )


@router.get("/logs")
def list_logs(
    user_id: str | None = None,
    limit: int = Query(20, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(DiaryLog).order_by(DiaryLog.id.desc())
    if user_id:
        q = q.filter(DiaryLog.user_id == user_id)

    rows = q.limit(limit).all()
    return [
        {
            "id": r.id,
            "ts": r.ts.isoformat(),
            "user_id": r.user_id,
            "preset": r.preset_used,
            "mood": r.mood_hint,
            "valence": r.valence,
            "emotions": r.emotions,
            "keywords": r.keywords,
            "summary": r.summary,
        }
        for r in rows
    ]
