from src.parsers.instagram import InstagramParser
from src.parsers.kakaotalk import KakaoTalkParser
from src.schemas.chat import ChatThread

PARSERS = [InstagramParser(), KakaoTalkParser()]

def parse_chat(payload, me_hint=None) -> ChatThread:
    for parser in PARSERS:
        if parser.can_handle(payload):
            return parser.parse(payload, me_hint)
    raise ValueError("지원되지 않는 채팅 형식입니다.")
