import time
from sqlalchemy.orm import Session
from .schemas import DiaryInput, DiaryReplyOutput
from .analyzer import analyze
from .guard import safety_scan
from .generator import generate_pair
from api.models import save_diary_log, get_user_preset

def run_pipeline(payload: DiaryInput) -> DiaryReplyOutput:
    # 기존 단독 실행(로그/DB 미사용) 유지
    return _run_core(payload, user_id=None, preset_override=None, db=None)

def run_pipeline_with_logging(
    payload: DiaryInput,
    *,
    user_id: str | None,
    preset_override: str | None,
    db: Session | None
) -> DiaryReplyOutput:
    return _run_core(payload, user_id=user_id, preset_override=preset_override, db=db)

def _run_core(payload: DiaryInput, *, user_id, preset_override, db: Session | None):
    t0 = time.time()

    # 1) 규칙 분석
    analysis = analyze(payload.text)

    # 2) 안전 스캔
    safety_flag, flags = safety_scan(payload.text)

    # 3) 프리셋/무드 결정 (우선순위: 요청 meta > 헤더 override > DB 저장 프리셋 > 기본 warm)
    preset = (payload.meta or {}).get("preset")
    if not preset and preset_override:
        preset = preset_override
    if not preset and db and user_id:
        from_db = get_user_preset(db, user_id)
        if from_db:
            preset = from_db
    preset = preset or "warm"

    mood = (payload.meta or {}).get("mood")
    if not mood and analysis.emotions:
        mood = "/".join(analysis.emotions[:2])

    # 4) 생성 (짧은/보통)
    reply_short, reply_normal = generate_pair(payload.text, mood, preset)

    if safety_flag:
        reply_short += "\n\n혹시 위험하다고 느껴지면, 가까운 사람이나 전문 상담/상담센터에 바로 연락하자."
        reply_normal += "\n\n지금이 힘든 만큼 도움을 받는 게 정말 중요해. 가까운 사람에게 이야기하거나, 전문 상담/상담센터에 연락해줘."

    out = DiaryReplyOutput(
        reply_short=reply_short,
        reply_normal=reply_normal,
        safety_flag=safety_flag,
        flags=flags,
        analysis=analysis,
    )

    # 5) 로그 저장
    if db:
        latency_ms = int((time.time() - t0) * 1000)
        save_diary_log(
            db,
            user_id=user_id,
            preset_used=preset,
            mood_hint=mood,
            text=payload.text,
            reply_short=out.reply_short,
            reply_normal=out.reply_normal,
            analysis=out.analysis.model_dump(),
            safety_flag=out.safety_flag,
            flags=out.flags,
            latency_ms=latency_ms,
        )

    return out
