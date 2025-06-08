# keyword-news-scraping

### 개요

구글 뉴스 탭에서 최근 며칠간의 기사 리스트를 크롤링한다. 평소에 하는 일의 품을 줄이고 커버하는 키워드 범위를 넓히는 것이 목적

### python 환경 설정

- library install하려면 `pip install -r requirements.txt` 사용
- Mac에서는 `stock_env`라는 환경 사용 중

### 텔레그램 봇 설정

1. **봇 생성**: Telegram에서 BotFather(@BotFather)에게 `/newbot` 명령어를 보내 봇을 생성
2. **토큰 획득**: 봇 생성 후 받은 토큰을 복사
3. **채팅 ID 획득**: 봇과 대화를 시작한 후, `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`에서 chat id 확인
4. **환경변수 설정**:
   - 프로젝트 루트 디렉토리에 `.env` 파일 생성
   - 다음 내용을 추가:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     TELEGRAM_CHAT_ID=your_chat_id_here
     ```
5. **테스트**: `python scripts/test_telegram.py` 실행하여 연결 테스트
