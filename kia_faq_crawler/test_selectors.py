#!/usr/bin/env python3
"""
기아자동차 FAQ 셀렉터 테스트 스크립트
"""

import asyncio
from playwright.async_api import async_playwright

URL = "https://www.kia.com/kr/customer-service/center/faq"
SEL = {
    "item": "li.cmp-accordion__item",
    "question": ":scope span.cmp-accordion__title",
    "answer": ":scope div.cmp-accordion__panel p",
}

async def test_selectors():
    """셀렉터 테스트 함수"""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # 헤드리스 모드 해제하여 확인
        page = await browser.new_page()
        
        try:
            print(f"페이지 이동 중: {URL}")
            await page.goto(URL, timeout=60_000)
            await page.wait_for_load_state("domcontentloaded")
            
            print("FAQ 아이템 찾는 중...")
            items = await page.locator(SEL["item"]).all()
            print(f"발견된 FAQ 아이템 수: {len(items)}")
            
            if not items:
                print("❌ FAQ 아이템을 찾을 수 없습니다.")
                return
            
            print("\n" + "="*80)
            print("첫 번째 FAQ 아이템 테스트:")
            print("="*80)
            
            # 첫 번째 아이템으로 테스트
            first_item = items[0]
            
            # 질문 추출
            question_element = await first_item.locator(SEL["question"]).first
            if question_element:
                question_text = await question_element.inner_text()
                print(f"질문: {question_text.strip()}")
            else:
                print("❌ 질문을 찾을 수 없습니다.")
                return
            
            # 답변 패널 상태 확인
            aria_expanded = await first_item.get_attribute("aria-expanded")
            print(f"답변 패널 상태: {aria_expanded}")
            
            # 답변 패널이 접혀 있으면 클릭
            if aria_expanded == "false":
                print("답변 패널 펼치는 중...")
                await question_element.click()
                await first_item.locator("div.cmp-accordion__panel").wait_for(state="attached")
                await asyncio.sleep(1)
            
            # 답변 추출
            answer_elements = await first_item.locator(SEL["answer"]).all()
            print(f"답변 요소 수: {len(answer_elements)}")
            
            answer_parts = []
            for answer_element in answer_elements:
                answer_text = await answer_element.inner_text()
                if answer_text.strip():
                    answer_parts.append(answer_text.strip())
            
            answer_text = "\n".join(answer_parts)
            print(f"답변: {answer_text}")
            
            if answer_text:
                print("✅ 셀렉터 테스트 성공!")
            else:
                print("❌ 답변을 찾을 수 없습니다.")
            
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_selectors()) 