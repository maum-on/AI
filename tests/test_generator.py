from diary_replier.generator import generate_reply

def test_generate_reply_returns_text(sample_text):
    analysis = {
        "valence": "neutral",
        "emotions": ["피곤", "성취"],
        "keywords": ["프레젠테이션", "피곤"],
        "summary": "발표를 마치고 성취감과 피곤함을 느낌"
    }
    out = generate_reply(sample_text, analysis, style="short")
    assert isinstance(out, str)
    assert len(out) > 0
