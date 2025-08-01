#!/usr/bin/env python3
"""
기타 카테고리 수정 스크립트
"""

import asyncio
from playwright.async_api import async_playwright

URL = "https://www.kia.com/kr/customer-service/center/faq"

async def fix_others_category():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("페이지 이동 중...")
            await page.goto(URL, timeout=60_000)
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(3)
            
            # 기타 카테고리 찾기 (마지막 카테고리)
            categories = await page.locator("span.name").all()
            others_category = categories[-1]  # 마지막 카테고리
            others_name = await others_category.inner_text()
            print(f"기타 카테고리: {others_name}")
            
            # 기타 카테고리 클릭
            await others_category.click()
            await asyncio.sleep(3)
            
            # FAQ 아이템들이 모두 로드될 때까지 대기
            print("FAQ 아이템 로딩 대기 중...")
            await page.wait_for_selector(".cmp-accordion__item", timeout=10000)
            await asyncio.sleep(2)  # 추가 대기
            
            # FAQ 아이템 찾기
            items = await page.locator(".cmp-accordion__item").all()
            print(f"발견된 FAQ 아이템 수: {len(items)}")
            
            if items:
                print("\n기타 카테고리 FAQ 목록:")
                faqs = []
                
                for i, item in enumerate(items):
                    try:
                        # 질문 추출
                        question_elements = await item.locator("span.cmp-accordion__title").all()
                        if question_elements and len(question_elements) > 0:
                            question = await question_elements[0].inner_text()
                            question = question.strip()
                            print(f"{i+1}. {question}")
                            
                            # 모든 FAQ를 클릭하여 답변 펼치기
                            await question_elements[0].click()
                            await asyncio.sleep(1.0)  # 답변 로딩 대기
                            
                            # 답변 추출 (다양한 셀렉터 시도)
                            answer = ""
                            
                            # 첫 번째 시도: 기본 셀렉터
                            answer_elements = await item.locator("div.cmp-accordion__panel p").all()
                            if answer_elements:
                                answer_parts = []
                                for answer_element in answer_elements:
                                    answer_text = await answer_element.inner_text()
                                    if answer_text.strip():
                                        answer_parts.append(answer_text.strip())
                                answer = "\n".join(answer_parts)
                            
                            # 두 번째 시도: 다른 셀렉터
                            if not answer:
                                answer_elements = await item.locator(".cmp-accordion__panel p").all()
                                if answer_elements:
                                    answer_parts = []
                                    for answer_element in answer_elements:
                                        answer_text = await answer_element.inner_text()
                                        if answer_text.strip():
                                            answer_parts.append(answer_text.strip())
                                    answer = "\n".join(answer_parts)
                            
                            # 세 번째 시도: div 요소
                            if not answer:
                                answer_elements = await item.locator("div.cmp-accordion__panel div").all()
                                if answer_elements:
                                    answer_parts = []
                                    for answer_element in answer_elements:
                                        answer_text = await answer_element.inner_text()
                                        if answer_text.strip():
                                            answer_parts.append(answer_text.strip())
                                    answer = "\n".join(answer_parts)
                            
                            # 디버깅: 답변 길이 출력
                            print(f"  답변 길이: {len(answer)}자")
                            if not answer:
                                print(f"  ❌ 답변을 찾을 수 없습니다.")
                            else:
                                print(f"  ✅ 답변 수집 완료")
                            
                            if question and answer:
                                faqs.append({
                                    "category": "기타",
                                    "question": question,
                                    "answer": answer
                                })
                    
                    except Exception as e:
                        print(f"FAQ {i+1} 처리 중 오류: {e}")
                
                print(f"\n총 수집된 FAQ: {len(faqs)}개")
                
                # JSON 파일로 저장
                import json
                from datetime import datetime
                
                data = {
                    "metadata": {
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "category": "기타",
                        "total_items": len(faqs)
                    },
                    "data": faqs
                }
                
                filename = f"data/processed/others_faq_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"기타 카테고리 FAQ 저장 완료: {filename}")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(fix_others_category()) 