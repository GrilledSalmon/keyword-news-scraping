import logging
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
from ..config.settings import (
    RAW_DATA_DIR,
    SAVE_FORMAT,
    ENCODING,
    LOG_DIR,
    LOG_LEVEL,
    LOG_FORMAT,
    EXCLUDED_SOURCES
)

# 로깅 설정
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_DIR / "crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoogleNewsCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.base_url = "https://www.google.com/search"

    def get_news_titles_by_page(self, keyword, page_num=1, time_period="d"):
        """
        구글 뉴스에서 특정 키워드의 n번째 페이지 기사 제목들을 가져옵니다.
        
        Args:
            keyword (str): 검색할 키워드
            page_num (int): 페이지 번호 (1부터 시작)
            time_period (str): 시간 범위 ('h'=시간, 'd'=일, 'w'=주, 'm'=월, 'y'=년)
            
        Returns:
            list: 뉴스 제목과 정보가 담긴 딕셔너리 리스트
        """
        try:
            # URL 파라미터 설정
            params = {
                'q': keyword,
                'tbm': 'nws',  # 뉴스 탭
                'tbs': f'qdr:{time_period}',  # 시간 범위
                'hl': 'ko',  # 한국어
                'gl': 'KR',  # 한국
                'start': (page_num - 1) * 10  # 페이지네이션 (0, 10, 20, ...)
            }
            
            logger.info(f"'{keyword}' 키워드의 {page_num}페이지 검색 중...")
            
            # 요청 보내기
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 기사 정보 추출
            articles = []
            
            # 구글 뉴스 결과에서 제목 추출 (더 정확한 선택자 사용)
            news_items = soup.find_all('div', {'class': 'SoaBEf'}) or \
                        soup.find_all('div', {'class': 'MjjYud'})
            
            # 뉴스 기사가 없으면 빈 리스트 반환
            if not news_items:
                logger.info(f"'{keyword}' {page_num}페이지에서 뉴스 기사를 찾을 수 없습니다.")
                return []
            
            for item in news_items:
                if not isinstance(item, Tag):
                    continue
                try:
                    # 링크 추출
                    link_elem = item.find('a')
                    link = ""
                    if isinstance(link_elem, Tag):
                        href_val = link_elem.get('href', '')
                        if isinstance(href_val, list):
                            link = ''.join(href_val)
                        else:
                            link = str(href_val)
                    
                    # 제목 추출 - HTML 구조에 따라 정확한 선택자 사용
                    title_elem = item.select_one('div[role="heading"]') or \
                                item.select_one('.n0jPhd.ynAwRc.MBeuO.nDgy9d') or \
                                item.select_one('h3')
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # 출처 추출 - 신문사 이름이 있는 정확한 위치
                    source_elem = item.select_one('.MgUUmf.NUnG9d span') or \
                                 item.select_one('.NUnG9d span') or \
                                 item.select_one('span.vr1PYe') or \
                                 item.select_one('cite')
                    source = source_elem.get_text(strip=True) if source_elem else ''
                    
                    # 내용 추출 - GI74Re 클래스 사용
                    content_elem = item.select_one('.GI74Re.nDgy9d') or \
                                  item.select_one('.GI74Re')
                    content = content_elem.get_text(strip=True) if content_elem else ''
                    
                    # 시간 추출 - OSrXXb 클래스 사용
                    time_elem = item.select_one('.OSrXXb.rbYSKb.LfVVr span') or \
                               item.select_one('.OSrXXb span') or \
                               item.select_one('.LfVVr span')
                    published_time = time_elem.get_text(strip=True) if time_elem else ''
                    
                    # 대안 방법으로 시간 정보 추출
                    if not published_time:
                        full_text = item.get_text(strip=True)
                        time_match = re.search(r'(\d+)\s*(시간|분|일|주|개월|년)\s*전', full_text)
                        if time_match:
                            published_time = time_match.group(0)
                    
                    # 제목이나 내용이 비어있으면 대안 방법 시도
                    if not title or not content:
                        # 전체 텍스트 분석
                        full_text = item.get_text(separator='|', strip=True)
                        if full_text:
                            # 시간 정보 제거
                            clean_text = re.sub(r'\d+\s*(시간|분|일|주|개월|년)\s*전', '', full_text).strip()
                            
                            # 파이프로 분리된 부분들 분석
                            parts = [part.strip() for part in clean_text.split('|') if part.strip()]
                            
                            if len(parts) >= 2:
                                # 언론사명 찾기
                                if not source:
                                    for part in parts:
                                        if len(part) < 20 and any(keyword in part for keyword in ['뉴스', '신문', '일보', '방송', '투데이', '헤럴드']):
                                            source = part
                                            break
                                
                                # 제목과 내용 분리
                                remaining_parts = [p for p in parts if p != source]
                                if len(remaining_parts) >= 2:
                                    if not title:
                                        title = remaining_parts[0]
                                    if not content:
                                        content = remaining_parts[1]
                    
                    # 제목과 내용이 비어있으면 건너뛰기
                    if not title:
                        continue
                    
                    # 최종 정리
                    title = title.strip()
                    content = content.strip()
                    source = source.strip()
                    published_time = published_time.strip()
                    
                    # 불필요한 문자 제거
                    title = re.sub(r'^["\'\[\]]+|["\'\[\]]+$', '', title)
                    source = re.sub(r'[^\w가-힣\s]', '', source)
                    
                    # 유효하지 않은 제목 필터링
                    invalid_titles = [
                        '필터 및 주제', '검색어(', '뉴스', '이미지', '동영상', '쇼핑',
                        '지도', '도서', '항공편', '금융', '모든 뉴스', '검색 도구',
                        '언제든지', '최근', '분류 기준', '관련성', '날짜', '언어',
                        'Google', '구글', '설정', '개인정보처리방침', '약관', '광고'
                    ]
                    
                    # 제목이 너무 짧거나 유효하지 않은 경우 건너뛰기
                    if (len(title) < 5 or 
                        title in invalid_titles or
                        any(invalid in title for invalid in invalid_titles) or
                        title.count('(') > title.count(')') or  # 괄호가 맞지 않는 경우
                        re.match(r'^[^\w가-힣]*$', title)):  # 특수문자만 있는 경우
                        continue
                    
                    # 링크가 구글 내부 링크가 아닌 실제 뉴스 링크인지 확인
                    if not link or 'google.com' in link or not link.startswith('http'):
                        continue
                    
                    # 제외할 언론사 필터링
                    if source and any(excluded.lower() in source.lower() for excluded in EXCLUDED_SOURCES):
                        continue
                    
                    # 시간 문자열을 숫자(시간 단위)로 변환
                    published_time_number = self._convert_time_to_hours(published_time)
                    
                    articles.append({
                        'title': title,
                        'content': content,
                        'link': link,
                        'source': source,
                        'published_time': published_time,
                        'published_time_number': published_time_number,
                        'keyword': keyword,
                        'page': page_num
                    })
                    
                except Exception as e:
                    logger.warning(f"기사 파싱 중 오류 발생: {e}")
                    continue
            
            # 중복 제거 (제목 기준)
            seen_titles = set()
            unique_articles = []
            for article in articles:
                if article['title'] not in seen_titles:
                    seen_titles.add(article['title'])
                    unique_articles.append(article)
            
            logger.info(f"'{keyword}' {page_num}페이지에서 {len(unique_articles)}개 기사 발견")
            return unique_articles
            
        except Exception as e:
            logger.error(f"뉴스 검색 중 오류 발생: {e}")
            return []

    def get_multiple_pages(self, keyword, max_pages=3, time_period="d"):
        """
        여러 페이지에서 뉴스를 수집합니다.
        
        Args:
            keyword (str): 검색할 키워드
            max_pages (int): 수집할 최대 페이지 수
            time_period (str): 시간 범위
            
        Returns:
            list: 모든 페이지의 뉴스 기사 리스트
        """
        all_articles = []
        
        for page in range(1, max_pages + 1):
            articles = self.get_news_titles_by_page(keyword, page, time_period)
            all_articles.extend(articles)
            
            if not articles:  # 더 이상 기사가 없으면 중단
                logger.info(f"{page}페이지에서 기사가 없어 수집을 중단합니다.")
                break
                
        return all_articles

    def save_articles(self, articles, keyword):
        """
        수집한 기사를 파일로 저장합니다.
        
        Args:
            articles (list): 저장할 기사 목록
            keyword (str): 검색 키워드
        """
        if not articles:
            logger.warning(f"'{keyword}'에 대한 기사가 없습니다.")
            return
            
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{keyword}_{timestamp}.{SAVE_FORMAT}"
        filepath = RAW_DATA_DIR / filename
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(articles)
        
        # 파일 저장
        if SAVE_FORMAT == "csv":
            df.to_csv(filepath, encoding=ENCODING, index=False)
        elif SAVE_FORMAT == "json":
            df.to_json(filepath, orient="records", force_ascii=False)
            
        logger.info(f"'{keyword}'에 대한 {len(articles)}개의 기사를 {filepath}에 저장했습니다.")

    def test_parsing(self, keyword="테스트", max_results=3):
        """
        파싱 결과를 테스트하기 위한 함수
        """
        articles = self.get_news_titles_by_page(keyword, page_num=1, time_period="d")
        
        print(f"\n=== '{keyword}' 검색 결과 (상위 {min(max_results, len(articles))}개) ===")
        for i, article in enumerate(articles[:max_results]):
            print(f"\n--- 기사 {i+1} ---")
            print(f"제목: {article['title']}")
            print(f"출처: {article['source']}")
            print(f"내용: {article['content']}")
            print(f"시간: {article['published_time']}")
            print(f"링크: {article['link'][:50]}..." if len(article['link']) > 50 else f"링크: {article['link']}")
        
        return articles

    @staticmethod
    def _convert_time_to_hours(time_str: str):
        """
        '7시간 전', '10분 전'과 같은 문자열을 시간(float) 단위로 변환한다.
        분 → 시간\n시간 → 시간\n일 → 24시간\n주 → 7*24시간\n개월 → 30*24시간(평균치)\n년 → 365*24시간(평균치)
        변환이 불가능하면 None 을 반환한다.
        """
        if not time_str:
            return None

        match = re.match(r"(\d+)\s*(분|시간|일|주|개월|년)\s*전", time_str)
        if not match:
            return None

        value = int(match.group(1))
        unit = match.group(2)

        if unit == '분':
            return round(value / 60, 3)
        if unit == '시간':
            return float(value)
        if unit == '일':
            return float(value * 24)
        if unit == '주':
            return float(value * 7 * 24)
        if unit == '개월':
            return float(value * 30 * 24)
        if unit == '년':
            return float(value * 365 * 24)
        return None

