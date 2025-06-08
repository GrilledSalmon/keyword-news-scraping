"""
텔레그램 봇을 이용한 메시지 전송 모듈
"""

import asyncio
import logging
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError

from ..config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramSender:
    """텔레그램 봇을 이용한 메시지 전송 클래스"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        텔레그램 봇 초기화
        
        Args:
            bot_token: 텔레그램 봇 토큰
            chat_id: 텔레그램 채팅 ID
        """
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        
        if not self.bot_token:
            raise ValueError("텔레그램 봇 토큰이 설정되지 않았습니다. TELEGRAM_BOT_TOKEN 환경변수를 설정하세요.")
        
        if not self.chat_id:
            raise ValueError("텔레그램 채팅 ID가 설정되지 않았습니다. TELEGRAM_CHAT_ID 환경변수를 설정하세요.")
        
        self.bot = Bot(token=self.bot_token)
    
    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        텔레그램으로 메시지 전송
        
        Args:
            message: 전송할 메시지
            parse_mode: 메시지 파싱 모드 (HTML, Markdown)
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"텔레그램 메시지 전송 성공: {message[:50]}...")
            return True
            
        except TelegramError as e:
            logger.error(f"텔레그램 메시지 전송 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"알 수 없는 오류로 메시지 전송 실패: {e}")
            return False
    
    def send_message_sync(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        동기 방식으로 텔레그램 메시지 전송
        
        Args:
            message: 전송할 메시지
            parse_mode: 메시지 파싱 모드
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_message(message, parse_mode))
    
    async def send_news_update(self, news_data: dict) -> bool:
        """
        뉴스 업데이트를 형식화하여 전송
        
        Args:
            news_data: 뉴스 데이터 딕셔너리
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            message = self._format_news_message(news_data)
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"뉴스 메시지 전송 중 오류: {e}")
            return False
    
    def _format_news_message(self, news_data: dict) -> str:
        """
        뉴스 데이터를 텔레그램 메시지 형식으로 변환
        
        Args:
            news_data: 뉴스 데이터
            
        Returns:
            str: 형식화된 메시지
        """
        title = news_data.get('title', '제목 없음')
        url = news_data.get('url', '')
        source = news_data.get('source', '출처 없음')
        published_time = news_data.get('published_time', '')
        
        message = f"""
🔔 <b>새로운 뉴스</b>

📰 <b>{title}</b>

🏢 출처: {source}
⏰ 시간: {published_time}

🔗 <a href="{url}">기사 읽기</a>
        """.strip()
        
        return message
    
    async def test_connection(self) -> bool:
        """
        텔레그램 봇 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        test_message = "🤖 텔레그램 봇 연결 테스트 성공!"
        return await self.send_message(test_message) 