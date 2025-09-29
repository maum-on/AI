from diary_replier.schemas import DiaryInput, DiaryReplyOutput, AnalysisResult
from diary_replier import guard, analyzer, generator

def diary_to_reply(payload: DiaryInput) -> DiaryReplyOutput:
    text, pii_flag = guard.mask_pii(payload.text.strip())
    crisis = guard.detect_crisis(text)
    if crisis:
        crisis_msg = (
            "지금 마음이 많이 힘들어 보이세요. "
            "당신의 안전이 가장 중요합니다. "
            "믿을 수 있는 사람과 꼭 연결되시길 권해요. "
            "긴급 상황이라면 지역의 긴급전화로 바로 연락해 주세요."
        )
        return DiaryReplyOutput(
            reply_short=crisis_msg,
            reply_normal=crisis_msg,
            safety_flag=True,
            flags={"crisis": True, "pii_detected": pii_flag},
            analysis=AnalysisResult(valence="negative", emotions=[], keywords=[], summary="위기 상황 탐지됨"),
        )

    # 긴 글 모드 판단: ① 옵션 long_mode="full" 이거나 ② 글자수 > 1000
    long_mode = (payload.meta.get("long_mode") == "full") if isinstance(payload.meta, dict) else False
    if long_mode or len(text) > 1000:
        analysis = analyzer.analyze_diary_long(text, max_chars_per_chunk=800)
        reply_short = generator.generate_reply(text, analysis, style="short")
        reply_normal = generator.generate_reply(text, analysis, style="normal")
    else:
        analysis = analyzer.analyze_diary(text)
        reply_short = generator.generate_reply(text, analysis, style="short")
        reply_normal = generator.generate_reply(text, analysis, style="normal")

    return DiaryReplyOutput(
        reply_short=reply_short,
        reply_normal=reply_normal,
        safety_flag=False,
        flags={"crisis": False, "pii_detected": pii_flag, "long_mode": long_mode or (len(text)>1000)},
        analysis=AnalysisResult(**{k:v for k,v in analysis.items() if not k.startswith("_")}),
    )
