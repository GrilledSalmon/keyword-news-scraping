#!/usr/bin/env python3
"""
텔레그램 봇 테스트 스크립트
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트를 sys.path에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# .env 파일 로드
env_path = ROOT_DIR / '.env'
load_dotenv(env_path)

from src.telegram_bot import TelegramSender


async def test_telegram_connection():
    """텔레그램 연결 테스트"""
    print("🔄 텔레그램 봇 연결 테스트 시작...")
    
    try:
        # 환경변수 확인
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        print(f"Bot Token: {bot_token[:10]}..." if bot_token else "Bot Token: None")
        print(f"Chat ID: {chat_id}")
        
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN 환경변수가 설정되지 않았습니다.")
            print("📝 .env 파일에 다음 내용을 추가하세요:")
            print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
            return False
        
        if not chat_id:
            print("❌ TELEGRAM_CHAT_ID 환경변수가 설정되지 않았습니다.")
            print("📝 .env 파일에 다음 내용을 추가하세요:")
            print("   TELEGRAM_CHAT_ID=your_chat_id_here")
            return False
        
        # 텔레그램 봇 초기화
        telegram_sender = TelegramSender()
        
        # 연결 테스트
        success = await telegram_sender.test_connection()
        
        if success:
            print("✅ 텔레그램 봇 연결 성공!")
            
            # 샘플 뉴스 메시지 테스트
            sample_news = {
                'title': '테스트 뉴스 제목',
                'url': 'https://example.com',
                'source': '테스트 뉴스통신',
                'published_time': '2024-01-01 12:00:00'
            }
            
            print("📰 샘플 뉴스 메시지 전송 테스트...")
            news_success = await telegram_sender.send_news_update(sample_news)
            
            if news_success:
                print("✅ 뉴스 메시지 전송 성공!")
            else:
                print("❌ 뉴스 메시지 전송 실패")
                
        else:
            print("❌ 텔레그램 봇 연결 실패")
            
        return success
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


def main():
    """메인 함수"""
    print("🤖 텔레그램 봇 테스트 프로그램")
    print("=" * 50)
    
    # 비동기 함수 실행
    result = asyncio.run(test_telegram_connection())
    
    if result:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n💥 테스트가 실패했습니다. 설정을 확인해주세요.")
        sys.exit(1)


if __name__ == "__main__":
    main() 