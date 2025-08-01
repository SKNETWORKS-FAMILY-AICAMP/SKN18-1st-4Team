#!/usr/bin/env python3
"""
기타 카테고리 확인 스크립트
"""

import asyncio
from playwright.async_api import async_playwright

URL = "https://www.kia.com/kr/customer-service/center/faq"

async def check_others_category():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("페이지 이동 중...")
            await page.goto(URL, timeout=60_000)
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(3)
            
            # 모든 카테고리 찾기
            categories = await page.locator("span.name").all()
            print(f"발견된 카테고리 수: {len(categories)}")
            
            # 카테고리명 출력
            print("\n카테고리 목록:")
            for i, cat in enumerate(categories):
                cat_name = await cat.inner_text()
                print(f"{i+1}. {cat_name}")
            
            # 기타 카테고리 찾기 (마지막 카테고리)
            if categories:
                others_index = len(categories) - 1
                others_category = categories[others_index]
                others_name = await others_category.inner_text()
                print(f"\n기타 카테고리: {others_name}")
                
                # 기타 카테고리 클릭
                await others_category.click()
                await asyncio.sleep(3)
                
                # FAQ 아이템 찾기
                items = await page.locator(".cmp-accordion__item").all()
                print(f"기타 카테고리 FAQ 수: {len(items)}")
                
                if items:
                    print("\n기타 카테고리 FAQ 목록:")
                    for i, item in enumerate(items[:5]):  # 처음 5개만 출력
                        question_element = await item.locator("span.cmp-accordion__title").first
                        if question_element:
                            question = await question_element.inner_text()
                            print(f"{i+1}. {question.strip()}")
                    
                    if len(items) > 5:
                        print(f"... 외 {len(items)-5}개 더")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_others_category()) 