#!/usr/bin/env python3
"""
페이지네이션 구조 디버깅 스크립트
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_pagination():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # 브라우저 표시
        page = await browser.new_page()
        
        print("페이지 이동 중...")
        await page.goto("https://www.kia.com/kr/customer-service/center/faq", timeout=60000)
        await asyncio.sleep(3)
        
        # 차량구매 카테고리 클릭 (39개가 있다고 하신 카테고리)
        print("차량구매 카테고리 클릭 중...")
        category_elements = await page.query_selector_all("span.name")
        if len(category_elements) >= 3:  # 차량구매는 3번째 인덱스
            await category_elements[2].click()
            await asyncio.sleep(3)
        
        print("=" * 60)
        print("페이지네이션 구조 분석")
        print("=" * 60)
        
        # 다양한 페이지네이션 셀렉터 시도
        pagination_selectors = [
            ".cmp-pagination",
            ".pagination", 
            "[class*='pagination']",
            "[class*='page']",
            "nav",
            ".pager",
            ".page-numbers",
            ".page-nav"
        ]
        
        for selector in pagination_selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"✅ 셀렉터 '{selector}'에서 {len(elements)}개 요소 발견")
                for i, elem in enumerate(elements):
                    try:
                        text = await elem.inner_text()
                        classes = await elem.get_attribute("class")
                        print(f"  요소 {i+1}: 클래스='{classes}', 텍스트='{text[:100]}...'")
                    except:
                        print(f"  요소 {i+1}: 텍스트 추출 실패")
            else:
                print(f"❌ 셀렉터 '{selector}'에서 요소 없음")
        
        print("\n" + "=" * 60)
        print("전체 페이지 HTML 구조 확인")
        print("=" * 60)
        
        # 페이지 하단 부분의 HTML 확인
        page_html = await page.content()
        
        # 페이지네이션 관련 키워드 검색
        pagination_keywords = ["pagination", "page", "next", "prev", "1", "2", "3", "4", "5"]
        
        for keyword in pagination_keywords:
            if keyword in page_html.lower():
                print(f"✅ 키워드 '{keyword}' 발견")
        
        # 페이지 하단 부분만 추출
        lines = page_html.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in pagination_keywords):
                print(f"라인 {i+1}: {line.strip()}")
        
        print("\n" + "=" * 60)
        print("FAQ 아이템 수 확인")
        print("=" * 60)
        
        # FAQ 아이템 수 확인
        faq_items = await page.query_selector_all(".cmp-accordion__item")
        print(f"현재 페이지 FAQ 아이템 수: {len(faq_items)}개")
        
        # 페이지 하단으로 스크롤
        print("페이지 하단으로 스크롤 중...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        
        # 스크롤 후 다시 FAQ 아이템 수 확인
        faq_items_after_scroll = await page.query_selector_all(".cmp-accordion__item")
        print(f"스크롤 후 FAQ 아이템 수: {len(faq_items_after_scroll)}개")
        
        await asyncio.sleep(5)  # 브라우저 유지
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_pagination()) 