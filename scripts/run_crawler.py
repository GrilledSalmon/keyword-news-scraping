import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.crawler.google_news import GoogleNewsCrawler
from src.config.settings import LOG_DIR, LOG_LEVEL, LOG_FORMAT

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

def main():
    # 크롤러 인스턴스 생성
    crawler = GoogleNewsCrawler()
    
    # 검색할 키워드 목록
    keywords = [
        "삼성전자",
        "SK하이닉스",
        "LG에너지솔루션",
        "현대차",
        "기아"
    ]
    
    # 검색 기간 설정 (어제부터 오늘까지)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    # 각 키워드에 대해 뉴스 검색 및 저장
    for keyword in keywords:
        logger.info(f"'{keyword}' 키워드에 대한 뉴스 검색을 시작합니다.")
        
        # 뉴스 검색
        articles = crawler.search_news(keyword, start_date, end_date)
        
        # 검색 결과 저장
        crawler.save_articles(articles, keyword)
        
        logger.info(f"'{keyword}' 키워드에 대한 뉴스 검색이 완료되었습니다.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"크롤러 실행 중 오류 발생: {e}")
        sys.exit(1) 