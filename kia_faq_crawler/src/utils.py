"""
기아자동차 FAQ 크롤링 유틸리티 함수들
"""

import logging
import time
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import re


def setup_logging(log_config: Dict[str, Any]) -> logging.Logger:
    """
    로깅 설정을 초기화합니다.
    
    Args:
        log_config: 로깅 설정 딕셔너리
        
    Returns:
        설정된 로거 객체
    """
    logger = logging.getLogger('kia_faq_crawler')
    logger.setLevel(getattr(logging, log_config['level']))
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(log_config['file'], encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷터 설정
    formatter = logging.Formatter(log_config['format'])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def clean_text(text: str) -> str:
    """
    텍스트를 정제합니다.
    
    Args:
        text: 정제할 텍스트
        
    Returns:
        정제된 텍스트
    """
    if not text:
        return ""
    
    # 공백 정리
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 특수 문자 정리
    text = re.sub(r'[\r\n\t]+', ' ', text)
    
    return text


async def safe_get_text(element, default: str = "") -> str:
    """
    요소에서 안전하게 텍스트를 추출합니다.
    
    Args:
        element: 텍스트를 추출할 요소
        default: 기본값
        
    Returns:
        추출된 텍스트 또는 기본값
    """
    try:
        if element:
            if hasattr(element, 'text_content'):
                text = await element.text_content()
            else:
                text = str(element)
            return clean_text(text.strip())
    except Exception:
        pass
    
    return default


def generate_id(text: str) -> str:
    """
    텍스트로부터 고유 ID를 생성합니다.
    
    Args:
        text: ID 생성에 사용할 텍스트
        
    Returns:
        생성된 ID
    """
    # 특수 문자 제거 및 소문자 변환
    id_text = re.sub(r'[^\w\s-]', '', text.lower())
    # 공백을 하이픈으로 변환
    id_text = re.sub(r'[-\s]+', '-', id_text)
    # 앞뒤 하이픈 제거
    id_text = id_text.strip('-')
    
    return id_text


def format_timestamp() -> str:
    """
    현재 시간을 포맷된 문자열로 반환합니다.
    
    Returns:
        포맷된 시간 문자열
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def safe_delay(delay: float) -> None:
    """
    안전한 지연을 수행합니다.
    
    Args:
        delay: 지연 시간 (초)
    """
    try:
        await asyncio.sleep(delay)
    except KeyboardInterrupt:
        raise
    except Exception:
        pass


def validate_url(url: str) -> bool:
    """
    URL이 유효한지 검증합니다.
    
    Args:
        url: 검증할 URL
        
    Returns:
        유효성 여부
    """
    if not url:
        return False
    
    # 기본적인 URL 패턴 검증
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def extract_category_from_text(text: str) -> str:
    """
    텍스트에서 카테고리명을 추출합니다.
    
    Args:
        text: 카테고리를 추출할 텍스트
        
    Returns:
        추출된 카테고리명
    """
    if not text:
        return "기타"
    
    # 일반적인 카테고리 패턴들
    category_patterns = [
        r'구매|주문|결제|계약',
        r'배송|인도|수령',
        r'정비|서비스|수리|점검',
        r'보증|보험|AS',
        r'충전|연료|주유',
        r'앱|서비스|기술',
        r'환불|교환|반품',
        r'기타|문의|상담'
    ]
    
    for pattern in category_patterns:
        if re.search(pattern, text):
            if '구매' in pattern or '주문' in pattern:
                return "구매/주문"
            elif '배송' in pattern or '인도' in pattern:
                return "배송/인도"
            elif '정비' in pattern or '서비스' in pattern:
                return "정비/서비스"
            elif '보증' in pattern or '보험' in pattern:
                return "보증/보험"
            elif '충전' in pattern or '연료' in pattern:
                return "충전/연료"
            elif '앱' in pattern or '서비스' in pattern:
                return "앱/서비스"
            elif '환불' in pattern or '교환' in pattern:
                return "환불/교환"
    
    return "기타" 