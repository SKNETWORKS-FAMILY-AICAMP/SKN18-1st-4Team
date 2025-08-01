#!/usr/bin/env python3
"""
셀렉터 디버깅 스크립트
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.async_api import async_playwright
import logging

async def debug_selectors():
    """현재 웹사이트의 셀렉터를 디버깅합니다."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("셀렉터 디버깅 시작...")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)  # 브라우저를 보이게 실행
        page = await browser.new_page()
        
        # 페이지 이동
        url = "https://www.kia.com/kr/customer-service/center/faq"
        logger.info(f"페이지 이동: {url}")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_load_state("domcontentloaded")
        
        # 잠시 대기 (수동으로 확인할 수 있도록)
        logger.info("페이지가 로드되었습니다. 브라우저를 확인해주세요.")
        await asyncio.sleep(10)
        
        # 다양한 셀렉터 시도
        selectors_to_try = [
            "span.name",
            ".name",
            "span",
            "button",
            ".cmp-accordion__item",
            "[class*='category']",
            "[class*='tab']",
            "[class*='menu']"
        ]
        
        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                logger.info(f"셀렉터 '{selector}': {len(elements)}개 요소 발견")
                
                if len(elements) > 0:
                    # 첫 번째 요소의 텍스트 출력
                    text = await elements[0].inner_text()
                    logger.info(f"  첫 번째 요소 텍스트: {text[:50]}...")
                    
                    # HTML 구조 확인
                    html = await elements[0].inner_html()
                    logger.info(f"  HTML 구조: {html[:100]}...")
                    
            except Exception as e:
                logger.warning(f"셀렉터 '{selector}' 실패: {e}")
        
        # 페이지 전체 HTML 구조 확인
        logger.info("페이지 전체 구조 확인 중...")
        body_html = await page.inner_html("body")
        logger.info(f"Body HTML 길이: {len(body_html)}")
        
        # FAQ 관련 요소 찾기
        faq_selectors = [
            ".cmp-accordion__item",
            "[class*='faq']",
            "[class*='accordion']",
            ".item",
            ".question"
        ]
        
        for selector in faq_selectors:
            try:
                elements = await page.query_selector_all(selector)
                logger.info(f"FAQ 셀렉터 '{selector}': {len(elements)}개 요소 발견")
            except Exception as e:
                logger.warning(f"FAQ 셀렉터 '{selector}' 실패: {e}")
        
        await asyncio.sleep(5)  # 결과 확인을 위한 대기
        
    except Exception as e:
        logger.error(f"디버깅 실패: {e}")
        raise
    
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_selectors()) 