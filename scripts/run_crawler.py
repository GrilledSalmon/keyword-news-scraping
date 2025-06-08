import sys
from pathlib import Path
import logging
import asyncio
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# .env 파일 로드
env_path = project_root / '.env'
load_dotenv(env_path)

from src.crawler.google_news import GoogleNewsCrawler
from src.config.settings import LOG_DIR, LOG_LEVEL, LOG_FORMAT
from src.telegram_bot import TelegramSender
from src.telegram_bot.message_formatter import send_articles_to_telegram

# 로깅 설정
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_DIR / "run_crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main_async():
    """비동기 메인 함수"""
    # 크롤러 인스턴스 생성
    crawler = GoogleNewsCrawler()
    
    # 텔레그램 봇 초기화
    try:
        telegram_sender = TelegramSender()
        logger.info("텔레그램 봇이 성공적으로 초기화되었습니다.")
        
        # 크롤링 시작 알림
        await telegram_sender.send_message("🤖 <b>뉴스 크롤링을 시작합니다!</b>")
        
    except Exception as e:
        logger.error(f"텔레그램 봇 초기화 실패: {e}")
        telegram_sender = None
    
    # 검색할 키워드 목록
    game_keywords = [
        "크래프톤",
        "시프트업",
        "네오위즈",
        "펄어비스",
        "붉은사막",
        "데브시스터즈",
    ]
    keywords = game_keywords + [
        "트럼프",
        "우크라",
        "이스라엘 이란",
        "인도 파키스탄",
        "WTI",
        "한한령",
        "예림당",
    ]
    MAX_PAGES = 3
    TIME_PERIOD = "d"
    
    total_articles = 0
    
    # 각 키워드에 대해 뉴스 검색 및 저장
    for keyword in keywords:
        logger.info(f"'{keyword}' 키워드에 대한 뉴스 검색을 시작합니다.")
        
        try:
            # 뉴스 검색
            articles = crawler.get_multiple_pages(keyword, MAX_PAGES, TIME_PERIOD)
            
            # 검색 결과 저장
            crawler.save_articles(articles, keyword)
            
            # 텔레그램으로 전송
            if telegram_sender:
                await send_articles_to_telegram(articles, keyword, telegram_sender)
                if articles:  # 기사가 있는 경우에만 카운트 증가
                    total_articles += len(articles)
                # 키워드 간 간격 (메시지 정리용)
                await asyncio.sleep(0.5)
            
            logger.info(f"'{keyword}' 키워드에 대한 뉴스 검색이 완료되었습니다. ({len(articles)}개 기사)")
            
        except Exception as e:
            logger.error(f"'{keyword}' 키워드 처리 중 오류: {e}")
            if telegram_sender:
                await telegram_sender.send_message(f"❌ <b>[{keyword}]</b>\n처리 중 오류 발생: {str(e)}")
    
    # 전체 완료 메시지
    if telegram_sender:
        completion_message = f"✅ <b>크롤링 완료</b>\n총 {total_articles}개 기사 수집"
        await telegram_sender.send_message(completion_message)
    
    logger.info(f"모든 크롤링이 완료되었습니다. 총 {total_articles}개 기사를 처리했습니다.")

def main():
    """메인 함수"""
    try:
        # 비동기 함수 실행
        asyncio.run(main_async())
    except Exception as e:
        logger.error(f"크롤러 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 