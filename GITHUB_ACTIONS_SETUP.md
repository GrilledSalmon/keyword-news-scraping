# GitHub Actions 자동 크롤링 설정 가이드

## 🚩 설정 완료!

매일 오후 11시(한국시간)에 자동으로 뉴스 크롤링이 실행되도록 GitHub Actions가 설정되었습니다.

## ⚙️ GitHub Secrets 설정 (필수)

GitHub에서 텔레그램 봇 정보를 안전하게 저장하기 위해 다음 단계를 따라주세요:

### 1. GitHub 저장소로 이동
- 본인의 GitHub 저장소 페이지로 이동

### 2. Settings 탭 클릭
- 저장소 상단의 "Settings" 탭 클릭

### 3. Secrets and variables 설정
- 왼쪽 메뉴에서 "Secrets and variables" → "Actions" 클릭

### 4. 다음 Secret들을 추가:

#### `TELEGRAM_BOT_TOKEN`
- "New repository secret" 클릭
- Name: `TELEGRAM_BOT_TOKEN`
- Secret: 텔레그램 봇 토큰 입력

#### `TELEGRAM_CHAT_ID`
- "New repository secret" 클릭  
- Name: `TELEGRAM_CHAT_ID`
- Secret: 텔레그램 채팅 ID 입력

## 🕐 실행 시간
- **매일 오전 7시 30분 (한국시간)** 자동 실행
- **매일 오후 11시 (한국시간)** 자동 실행
- 수동 실행도 가능: Actions 탭 → "Daily News Crawler" → "Run workflow"

## 📊 실행 확인 방법
1. GitHub 저장소 → "Actions" 탭
2. "Daily News Crawler" 워크플로우 클릭
3. 실행 상태 및 로그 확인 가능

## 🔧 장점
- ✅ **완전 무료** (월 2000분 제한, 충분함)
- ✅ **서버 관리 불필요**
- ✅ **안정적인 실행**
- ✅ **로그 자동 저장** (30일간)
- ✅ **수동 실행 가능**

## 🚨 주의사항
- GitHub 저장소가 private이어야 안전합니다
- Secrets는 절대 코드에 직접 작성하지 마세요
- 첫 실행 전 수동으로 한 번 테스트해보세요

## 🧪 테스트 방법
1. GitHub → Actions → "Daily News Crawler"
2. "Run workflow" 버튼 클릭
3. 실행 결과 확인

설정 완료 후 텔레그램으로 알림이 정상적으로 오는지 확인해주세요! 