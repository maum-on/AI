# src/parsers/instagram.py

from typing import Dict, Any, List, Optional
from .base import normalize_generic_chat


def parse_instagram_like(
    data: Dict[str, Any],
    me_hint: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    사실상 Meta export 형식은 전부 generic 파서로 처리.
    """
    return normalize_generic_chat(data, me_hint)
