import logging
import asyncio

logger = logging.getLogger(__name__)

async def format_article_message(articles, keyword, msg_num, total_messages, start_idx, include_published_time=True):
    """
    기사 목록을 텔레그램 메시지 형식으로 변환하는 공통 함수
    
    Args:
        articles: 기사 목록
        keyword: 검색 키워드
        msg_num: 현재 메시지 번호
        total_messages: 전체 메시지 수
        start_idx: 시작 인덱스
        include_published_time: 발행 시간 포함 여부
    """
    header = f"<b>[{keyword}] {msg_num + 1}/{total_messages}</b>"
    message_lines = [header, ""]
    
    for i, article in enumerate(articles, start_idx + 1):
        title = article.get('title', '제목 없음')
        link = article.get('link', '')
        source = article.get('source', '출처 없음')
        published_time = article.get('published_time', '시간 없음')
        
        # HTML 특수문자 이스케이핑
        title_escaped = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        article_line = f'{i}. {title_escaped}'
        
        if include_published_time:
            info_line = f'   📍 {source} | {published_time}'
        else:
            info_line = f"   📍 {source}"

        if link and link.startswith('http'):
            info_line += f' | <a href="{link}">[링크]</a>'
        
        message_lines.append(article_line)
        message_lines.append(info_line)
        message_lines.append("")
    
    if message_lines and message_lines[-1] == "":
        message_lines.pop()
    
    return "\n".join(message_lines)

async def send_articles_to_telegram(articles, keyword, telegram_sender):
    """
    크롤링한 기사들을 텔레그램으로 전송 (모든 기사 포함, 필요시 여러 메시지로 분할)
    """
    if not articles:
        logger.info(f"'{keyword}' 키워드에 대한 새로운 기사가 없습니다.")
        try:
            message = f"🔍 <b>[{keyword}]</b>\n\n새로운 기사가 없습니다."
            await telegram_sender.send_message(message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"'{keyword}' 키워드 메시지 전송 중 오류: {e}")
        return
    
    articles_per_message = 10
    total_messages = (len(articles) + articles_per_message - 1) // articles_per_message
    
    for msg_num in range(total_messages):
        start_idx = msg_num * articles_per_message
        end_idx = min((msg_num + 1) * articles_per_message, len(articles))
        current_articles = articles[start_idx:end_idx]
        message = await format_article_message(
            current_articles, keyword, msg_num, total_messages,
            start_idx, include_published_time=True
        )
        
        if len(message) > 4000:
            articles_per_message = max(5, articles_per_message - 2)
            logger.warning(f"메시지가 너무 길어서 기사 수를 {articles_per_message}개로 줄입니다.")
            await send_articles_to_telegram_split(articles, keyword, telegram_sender, articles_per_message)
            return
        
        try:
            success = await telegram_sender.send_message(message, parse_mode="HTML")
            if success:
                logger.info(f"'{keyword}' 키워드 뉴스 목록 전송 성공 ({len(current_articles)}개 기사, {msg_num + 1}/{total_messages})")
            else:
                logger.error(f"'{keyword}' 키워드 뉴스 목록 전송 실패 ({msg_num + 1}/{total_messages})")
            
            if msg_num < total_messages - 1:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"'{keyword}' 키워드 메시지 전송 중 오류: {e}")
            try:
                simple_message = f"[{keyword}] {msg_num + 1}/{total_messages}\n❌ 링크 포함 메시지 전송 실패, 텍스트만 전송"
                await telegram_sender.send_message(simple_message, parse_mode=None)
            except:
                pass

async def send_articles_to_telegram_split(articles, keyword, telegram_sender, articles_per_message):
    """
    기사를 지정된 수로 분할하여 전송하는 보조 함수
    """
    total_messages = (len(articles) + articles_per_message - 1) // articles_per_message
    
    for msg_num in range(total_messages):
        start_idx = msg_num * articles_per_message
        end_idx = min((msg_num + 1) * articles_per_message, len(articles))
        current_articles = articles[start_idx:end_idx]
        
        message = await format_article_message(
            current_articles, keyword, msg_num, total_messages,
            start_idx, include_published_time=False
        )
        
        try:
            success = await telegram_sender.send_message(message, parse_mode="HTML")
            if success:
                logger.info(f"'{keyword}' 분할 메시지 전송 성공 ({msg_num + 1}/{total_messages})")
            
            if msg_num < total_messages - 1:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"'{keyword}' 분할 메시지 전송 오류: {e}")
            try:
                simple_message = f"[{keyword}] {msg_num + 1}/{total_messages}\n❌ 링크 메시지 전송 실패"
                await telegram_sender.send_message(simple_message, parse_mode=None)
            except:
                pass 