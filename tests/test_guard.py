from diary_replier import guard

def test_mask_pii_phone():
    text, flagged = guard.mask_pii("내 번호는 010-1234-5678 이야.")
    assert "[민감정보]" in text
    assert flagged is True

def test_mask_pii_email():
    text, flagged = guard.mask_pii("메일은 test@example.com 으로 주세요.")
    assert "[민감정보]" in text
    assert flagged is True

def test_detect_crisis_positive():
    assert guard.detect_crisis("나 정말 죽고 싶어...") is True

def test_detect_crisis_negative():
    assert guard.detect_crisis("오늘은 피곤했어.") is False
