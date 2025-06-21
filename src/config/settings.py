from pathlib import Path
import os

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent.parent.parent

# 데이터 디렉토리
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# 크롤링 설정
CRAWLING_INTERVAL = 3600  # 1시간마다 크롤링
MAX_RETRIES = 3
TIMEOUT = 30

# 제외할 언론사 리스트
EXCLUDED_SOURCES = ["MSN", "네이트 뉴스"]

# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# 데이터 저장 설정
SAVE_FORMAT = "csv"  # or "json"
ENCODING = "utf-8"

# 로깅 설정
LOG_DIR = ROOT_DIR / "logs"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 디렉토리 생성
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True) 