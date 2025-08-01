#!/usr/bin/env python3
"""
HTML 구조 디버깅 스크립트
"""

import asyncio
from playwright.async_api import async_playwright

URL = "https://www.kia.com/kr/customer-service/center/faq"

async def debug_structure():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("페이지 이동 중...")
            await page.goto(URL, timeout=60_000)
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(3)
            
            # 카테고리 클릭
            categories = await page.locator("span.name").all()
            if categories:
                await categories[0].click()
                await asyncio.sleep(3)
                
                # FAQ 아이템 찾기 (li 태그 없이)
                items = await page.locator(".cmp-accordion__item").all()
                print(f"발견된 FAQ 아이템 수: {len(items)}")
                
                if items:
                    # 첫 번째 아이템의 HTML 구조 확인
                    first_item = items[0]
                    item_html = await first_item.inner_html()
                    item_tag = await first_item.evaluate("el => el.tagName")
                    item_classes = await first_item.evaluate("el => el.className")
                    
                    print(f"\n첫 번째 아이템 정보:")
                    print(f"태그: {item_tag}")
                    print(f"클래스: {item_classes}")
                    print(f"HTML 구조:")
                    print(item_html[:500] + "..." if len(item_html) > 500 else item_html)
                    
                    # 질문과 답변 요소 찾기
                    question_elements = await first_item.locator("span.cmp-accordion__title").all()
                    print(f"\n질문 요소 수: {len(question_elements)}")
                    
                    if question_elements:
                        question_text = await question_elements[0].inner_text()
                        print(f"질문: {question_text.strip()}")
                    
                    # 답변 패널 상태 확인
                    aria_expanded = await first_item.get_attribute("aria-expanded")
                    print(f"답변 패널 상태: {aria_expanded}")
                    
                    # 답변 요소 찾기
                    answer_elements = await first_item.locator("div.cmp-accordion__panel p").all()
                    print(f"답변 요소 수: {len(answer_elements)}")
                    
                    if answer_elements:
                        for i, answer in enumerate(answer_elements):
                            answer_text = await answer.inner_text()
                            print(f"답변 {i+1}: {answer_text.strip()}")
                    else:
                        print("답변 요소를 찾을 수 없습니다.")
                        
                        # 다른 답변 셀렉터 시도
                        print("\n다른 답변 셀렉터 시도:")
                        answer_selectors = [
                            ".cmp-accordion__panel p",
                            ".cmp-accordion__panel div",
                            ".cmp-accordion__content p",
                            ".accordion-content p"
                        ]
                        
                        for selector in answer_selectors:
                            elements = await first_item.locator(selector).all()
                            if elements:
                                print(f"✅ '{selector}'로 {len(elements)}개 요소 발견!")
                                for elem in elements:
                                    text = await elem.inner_text()
                                    print(f"  - {text.strip()}")
                            else:
                                print(f"❌ '{selector}'로 요소를 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_structure()) 