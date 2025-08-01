#!/usr/bin/env python3
"""
간단한 FAQ 테스트 스크립트
"""

import asyncio
from playwright.async_api import async_playwright

URL = "https://www.kia.com/kr/customer-service/center/faq"

async def simple_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # 브라우저 창을 보면서 확인
        page = await browser.new_page()
        
        try:
            print("페이지 이동 중...")
            await page.goto(URL, timeout=60_000)
            await page.wait_for_load_state("domcontentloaded")
            
            print("페이지 로딩 완료")
            await asyncio.sleep(3)  # 추가 대기
            
            # 카테고리 찾기
            print("카테고리 찾는 중...")
            categories = await page.locator("span.name").all()
            print(f"발견된 카테고리 수: {len(categories)}")
            
            if categories:
                # 첫 번째 카테고리 클릭
                print("첫 번째 카테고리 클릭 중...")
                await categories[0].click()
                await asyncio.sleep(3)  # 로딩 대기
                
                # FAQ 아이템 찾기
                print("FAQ 아이템 찾는 중...")
                items = await page.locator("li.cmp-accordion__item").all()
                print(f"발견된 FAQ 아이템 수: {len(items)}")
                
                if items:
                    print("✅ FAQ 아이템 발견!")
                    # 첫 번째 아이템 정보 출력
                    first_item = items[0]
                    question = await first_item.locator("span.cmp-accordion__title").inner_text()
                    print(f"첫 번째 질문: {question.strip()}")
                else:
                    print("❌ FAQ 아이템을 찾을 수 없습니다.")
                    
                    # 페이지의 HTML 구조 확인
                    print("\n페이지 구조 확인 중...")
                    body_html = await page.inner_html("body")
                    if "cmp-accordion__item" in body_html:
                        print("✅ 'cmp-accordion__item' 클래스가 페이지에 존재합니다.")
                    else:
                        print("❌ 'cmp-accordion__item' 클래스가 페이지에 없습니다.")
                        
                    # 다른 가능한 셀렉터들 시도
                    print("\n다른 셀렉터 시도 중...")
                    selectors_to_try = [
                        ".cmp-accordion__item",
                        "li[class*='accordion']",
                        ".accordion-item",
                        "[data-testid*='faq']",
                        ".faq-item"
                    ]
                    
                    for selector in selectors_to_try:
                        elements = await page.locator(selector).all()
                        if elements:
                            print(f"✅ '{selector}'로 {len(elements)}개 요소 발견!")
                        else:
                            print(f"❌ '{selector}'로 요소를 찾을 수 없습니다.")
            else:
                print("❌ 카테고리를 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_test()) 