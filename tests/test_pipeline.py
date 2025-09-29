from diary_replier.pipeline import diary_to_reply
from diary_replier.schemas import DiaryInput

def test_pipeline_normal_flow(sample_text):
    payload = DiaryInput(text=sample_text, user_id="u1")
    out = diary_to_reply(payload)

    # 필수 필드
    assert hasattr(out, "reply_short")
    assert hasattr(out, "reply_normal")
    assert hasattr(out, "safety_flag")
    assert hasattr(out, "flags")
    assert hasattr(out, "analysis")

    # 형식 검사
    assert isinstance(out.reply_short, str)
    assert isinstance(out.reply_normal, str)
    assert isinstance(out.safety_flag, bool)
    assert isinstance(out.flags, dict)
    assert out.analysis.valence in {"positive", "neutral", "negative"}

def test_pipeline_crisis_flow(crisis_text):
    payload = DiaryInput(text=crisis_text)
    out = diary_to_reply(payload)

    assert out.safety_flag is True
    assert out.flags.get("crisis") is True
    assert isinstance(out.reply_short, str)
    # 위기 템플릿은 보통 short/normal 동일 처리
    assert out.reply_short == out.reply_normal
