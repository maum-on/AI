from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import json

router = APIRouter(
    prefix="/chat-diary",
    tags=["chat-diary"],
)


@router.post("/chat-to-diary")
async def chat_to_diary(
    file: UploadFile = File(..., description="JSON 파일 업로드"),
    me_hint: str = Form("", description="사용자 힌트(optional)"),
):
    """
    디버깅 전용 endpoint.
    업로드된 JSON 파일을 파싱하여 최상위 key 목록을 반환한다.
    ingest / parser 로직은 생략한 간단한 확인 용도.

    - file: JSON 파일
    - me_hint: 선택적인 텍스트 힌트
    """
    # 파일 확장자 체크 (기본적인 안전장치)
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(
            status_code=400,
            detail="JSON 파일만 업로드할 수 있습니다 (.json)."
        )

    # 파일 읽기 및 JSON 파싱
    try:
        contents = await file.read()
        raw = json.loads(contents)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"JSON 파싱 실패: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"파일 처리 중 오류 발생: {e}"
        )

    # 반환 데이터 구성
    result = {
        "raw_keys": list(raw.keys()),
        "me_hint": me_hint or None,
        "file_name": file.filename,
    }

    return JSONResponse(result)
