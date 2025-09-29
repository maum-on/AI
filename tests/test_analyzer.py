from diary_replier.analyzer import analyze_diary

def test_analyze_diary_basic(sample_text):
    res = analyze_diary(sample_text)
    # 최소 필드 보장
    assert isinstance(res, dict)
    assert res.get("valence") in {"positive", "neutral", "negative"}
    assert isinstance(res.get("emotions"), list)
    assert isinstance(res.get("keywords"), list)
    assert isinstance(res.get("summary"), str)
