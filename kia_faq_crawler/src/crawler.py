"""
기아자동차 FAQ 크롤링 메인 클래스
"""

import asyncio
from playwright.async_api import async_playwright, Browser, Page
from typing import List, Dict, Any, Optional
import logging
import time
from .utils import safe_delay, safe_get_text, format_timestamp, validate_url


class KiaFAQCrawler:
    """
    기아자동차 FAQ 크롤링 메인 클래스
    """
    
    def __init__(self, 
                 website_url: str = "https://www.kia.com/kr/customer-service/center/faq",
                 selectors: Dict[str, str] = None,
                 browser_config: Dict[str, Any] = None,
                 crawling_config: Dict[str, Any] = None,
                 logger: Optional[logging.Logger] = None):
        """
        KiaFAQCrawler 초기화
        
        Args:
            website_url: 크롤링할 웹사이트 URL
            selectors: CSS 셀렉터 딕셔너리
            browser_config: 브라우저 설정
            crawling_config: 크롤링 설정
            logger: 로거 객체
        """
        self.website_url = website_url
        self.selectors = selectors or {
            "category": "span.name",
            "item": ".cmp-accordion__item",
            "question": ":scope span.cmp-accordion__title",
            "answer": ":scope div.cmp-accordion__panel p",
            "answer_links": ":scope div.cmp-accordion__panel a"
        }
        self.browser_config = browser_config or {
            "headless": True,
            "slow_mo": 100,
            "timeout": 30000
        }
        self.crawling_config = crawling_config or {
            "delay_between_requests": 1.0,
            "max_retries": 3,
            "retry_delay": 2.0
        }
        self.logger = logger or logging.getLogger(__name__)
        
        # 크롤링 결과
        self.categories = []
        self.faq_data = []
        self.browser = None
        self.page = None
        self.playwright = None
    
    async def setup_browser(self) -> Browser:
        """
        Playwright 브라우저를 설정합니다.
        
        Returns:
            설정된 브라우저 객체
        """
        try:
            self.logger.info("브라우저 설정 시작...")
            
            self.playwright = await async_playwright().start()
            
            # 브라우저 옵션 설정
            browser_options = {
                "headless": self.browser_config.get("headless", True),
                "slow_mo": self.browser_config.get("slow_mo", 100)
            }
            
            self.browser = await self.playwright.chromium.launch(**browser_options)
            
            # 페이지 생성
            self.page = await self.browser.new_page()
            
            # 타임아웃 설정
            timeout = self.browser_config.get("timeout", 30000)
            self.page.set_default_timeout(timeout)
            
            # User-Agent 설정
            await self.page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            
            self.logger.info("브라우저 설정 완료")
            return self.browser
            
        except Exception as e:
            self.logger.error(f"브라우저 설정 실패: {e}")
            raise
    
    async def navigate_to_page(self) -> bool:
        """
        FAQ 페이지로 이동합니다.
        
        Returns:
            이동 성공 여부
        """
        try:
            self.logger.info(f"페이지 이동: {self.website_url}")
            
            if not validate_url(self.website_url):
                raise ValueError(f"유효하지 않은 URL: {self.website_url}")
            
            if not self.page:
                raise ValueError("페이지가 초기화되지 않았습니다.")
            
            # 페이지 이동
            await self.page.goto(self.website_url, wait_until="networkidle")
            
            # 페이지 로딩 대기
            await self.page.wait_for_load_state("domcontentloaded")
            
            # 추가 대기 (동적 콘텐츠 로딩)
            await safe_delay(2.0)
            
            self.logger.info("페이지 이동 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"페이지 이동 실패: {e}")
            return False
    
    async def get_categories(self) -> List[Dict[str, str]]:
        """
        카테고리 목록을 수집합니다.
        
        Returns:
            카테고리 정보 리스트
        """
        try:
            self.logger.info("카테고리 수집 시작...")
            
            # 카테고리 셀렉터로 요소들 찾기
            category_elements = await self.page.query_selector_all(self.selectors["category"])
            
            categories = []
            for i, element in enumerate(category_elements):
                try:
                    category_name = await element.inner_text()
                    if category_name and category_name.strip():
                        category_info = {
                            "category_id": f"category_{i+1}",
                            "category_name": category_name.strip(),
                            "index": i
                        }
                        categories.append(category_info)
                        self.logger.info(f"카테고리 발견: {category_name.strip()}")
                except Exception as e:
                    self.logger.warning(f"카테고리 추출 실패 (인덱스 {i}): {e}")
            
            self.categories = categories
            self.logger.info(f"카테고리 수집 완료: {len(categories)}개")
            return categories
            
        except Exception as e:
            self.logger.error(f"카테고리 수집 실패: {e}")
            return []
    
    async def click_category(self, category_index: int) -> bool:
        """
        특정 카테고리를 클릭합니다.
        
        Args:
            category_index: 클릭할 카테고리 인덱스
            
        Returns:
            클릭 성공 여부
        """
        try:
            # 카테고리 요소들 다시 찾기
            category_elements = await self.page.query_selector_all(self.selectors["category"])
            
            if category_index >= len(category_elements):
                self.logger.warning(f"카테고리 인덱스 범위 초과: {category_index}")
                return False
            
            # 카테고리 클릭
            await category_elements[category_index].click()
            
            # 클릭 후 대기
            await safe_delay(self.crawling_config.get("delay_between_requests", 1.0))
            
            # 동적 콘텐츠 로딩 대기
            await self.page.wait_for_load_state("networkidle")
            
            self.logger.info(f"카테고리 클릭 완료: 인덱스 {category_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"카테고리 클릭 실패 (인덱스 {category_index}): {e}")
            return False
    
    async def get_faqs_by_category(self, category_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        특정 카테고리의 FAQ를 수집합니다 (페이지네이션 포함).
        
        Args:
            category_info: 카테고리 정보
            
        Returns:
            FAQ 데이터 리스트
        """
        try:
            category_name = category_info["category_name"]
            category_index = category_info["index"]
            
            self.logger.info(f"FAQ 수집 시작: {category_name}")
            
            # 카테고리 클릭
            if not await self.click_category(category_index):
                return []
            
            # 페이지네이션 정보 확인
            pagination_info = await self.get_pagination_info()
            total_pages = pagination_info["total_pages"]
            
            self.logger.info(f"카테고리 '{category_name}' - 총 {total_pages}페이지 발견")
            
            all_faqs = []
            question_counter = 0
            
            # 모든 페이지 순회
            for page_num in range(1, total_pages + 1):
                self.logger.info(f"페이지 {page_num}/{total_pages} 처리 중...")
                
                # 첫 페이지가 아닌 경우 페이지 이동
                if page_num > 1:
                    if not await self.go_to_page(page_num):
                        self.logger.warning(f"페이지 {page_num}로 이동 실패, 다음 페이지로 진행")
                        continue
                
                # 현재 페이지의 FAQ 아이템들 찾기
                item_elements = await self.page.query_selector_all(self.selectors["item"])
                
                self.logger.info(f"페이지 {page_num}에서 {len(item_elements)}개 FAQ 발견")
                
                for i, item_element in enumerate(item_elements):
                    try:
                        # 질문 텍스트 추출
                        question_element = await item_element.query_selector(self.selectors["question"])
                        if not question_element:
                            continue
                            
                        question_text = await safe_get_text(question_element)
                        if not question_text:
                            continue
                        
                        # 답변 패널이 접혀 있으면 클릭으로 펼치기
                        button_element = await item_element.query_selector("button.cmp-accordion__button")
                        if button_element:
                            aria_expanded = await button_element.get_attribute("aria-expanded")
                            if aria_expanded == "false":
                                await question_element.click()
                                # 답변 패널이 나타날 때까지 대기
                                await item_element.wait_for_selector("div.cmp-accordion__panel", state="attached")
                                await safe_delay(0.5)  # 답변 로딩 대기
                        
                        # 답변 요소들 찾기 (해당 아이템 내에서)
                        answer_elements = await item_element.query_selector_all(self.selectors["answer"])
                        
                        answer_parts = []
                        for answer_element in answer_elements:
                            answer_text = await safe_get_text(answer_element)
                            if answer_text.strip():
                                answer_parts.append(answer_text.strip())
                        
                        answer_text = "\n".join(answer_parts)
                        
                        # 링크 요소들 찾기 (해당 아이템 내에서)
                        link_elements = await item_element.query_selector_all(self.selectors["answer_links"])
                        
                        links = []
                        for link_element in link_elements:
                            try:
                                link_text = await safe_get_text(link_element)
                                link_href = await link_element.get_attribute("href")
                                if link_text.strip() and link_href:
                                    links.append({
                                        "text": link_text.strip(),
                                        "url": link_href
                                    })
                            except Exception as e:
                                self.logger.warning(f"링크 추출 실패: {e}")
                        
                        if question_text and answer_text:
                            faq_item = {
                                "category": category_name,
                                "category_id": category_info["category_id"],
                                "question": question_text,
                                "answer": answer_text,
                                "links": links,
                                "question_id": f"q_{category_index}_{question_counter}",
                                "page_number": page_num,
                                "created_at": format_timestamp()
                            }
                            all_faqs.append(faq_item)
                            question_counter += 1
                            
                            self.logger.info(f"FAQ 수집 (페이지 {page_num}): {question_text[:50]}...")
                        
                    except Exception as e:
                        self.logger.warning(f"FAQ 추출 실패 (카테고리: {category_name}, 페이지: {page_num}, 인덱스: {i}): {e}")
                
                # 페이지 간 대기
                if page_num < total_pages:
                    await safe_delay(0.5)
            
            self.logger.info(f"FAQ 수집 완료: {category_name} - 총 {len(all_faqs)}개 (총 {total_pages}페이지)")
            return all_faqs
            
        except Exception as e:
            self.logger.error(f"FAQ 수집 실패 (카테고리: {category_name}): {e}")
            return []
    
    async def crawl_all_categories(self) -> List[Dict[str, Any]]:
        """
        모든 카테고리의 FAQ를 수집합니다.
        
        Returns:
            전체 FAQ 데이터 리스트
        """
        try:
            self.logger.info("전체 카테고리 크롤링 시작...")
            
            all_faqs = []
            
            # 카테고리 목록 수집
            categories = await self.get_categories()
            if not categories:
                self.logger.error("카테고리를 찾을 수 없습니다.")
                return []
            
            # 각 카테고리별 FAQ 수집
            for i, category in enumerate(categories):
                try:
                    self.logger.info(f"카테고리 처리 중 ({i+1}/{len(categories)}): {category['category_name']}")
                    
                    faqs = await self.get_faqs_by_category(category)
                    all_faqs.extend(faqs)
                    
                    # 카테고리 간 딜레이
                    if i < len(categories) - 1:
                        await safe_delay(self.crawling_config.get("delay_between_requests", 1.0))
                    
                except Exception as e:
                    self.logger.error(f"카테고리 처리 실패 ({category['category_name']}): {e}")
                    continue
            
            self.faq_data = all_faqs
            self.logger.info(f"전체 크롤링 완료: {len(all_faqs)}개 FAQ")
            return all_faqs
            
        except Exception as e:
            self.logger.error(f"전체 크롤링 실패: {e}")
            return []
    
    async def run(self) -> List[Dict[str, Any]]:
        """
        크롤링을 실행합니다.
        
        Returns:
            수집된 FAQ 데이터
        """
        try:
            self.logger.info("기아자동차 FAQ 크롤링 시작")
            
            # 1. 브라우저 설정
            await self.setup_browser()
            
            # 2. 페이지 이동
            if not await self.navigate_to_page():
                raise Exception("페이지 이동 실패")
            
            # 3. 전체 카테고리 크롤링
            faq_data = await self.crawl_all_categories()
            
            self.logger.info(f"크롤링 완료: {len(faq_data)}개 FAQ 수집")
            return faq_data
            
        except Exception as e:
            self.logger.error(f"크롤링 실행 실패: {e}")
            raise
        
        finally:
            # 브라우저 정리
            await self.cleanup()
    
    async def cleanup(self):
        """브라우저 리소스를 정리합니다."""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("브라우저 정리 완료")
        except Exception as e:
            self.logger.warning(f"브라우저 정리 중 오류: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        크롤링 결과 요약을 반환합니다.
        
        Returns:
            크롤링 결과 요약
        """
        return {
            "total_categories": len(self.categories),
            "total_faqs": len(self.faq_data),
            "categories": [cat["category_name"] for cat in self.categories],
            "crawling_time": format_timestamp()
        } 

    async def get_pagination_info(self) -> Dict[str, Any]:
        """
        현재 페이지의 페이지네이션 정보를 가져옵니다.
        
        Returns:
            페이지네이션 정보 (총 페이지 수, 현재 페이지 등)
        """
        try:
            # 페이지네이션 컨테이너 확인
            pagination_container = await self.page.query_selector(self.selectors["pagination"]["container"])
            if not pagination_container:
                return {"has_pagination": False, "total_pages": 1, "current_page": 1}
            
            # 페이지 번호들 찾기
            page_elements = await self.page.query_selector_all(self.selectors["pagination"]["page_numbers"])
            
            if not page_elements:
                return {"has_pagination": False, "total_pages": 1, "current_page": 1}
            
            # 현재 페이지 확인
            current_page_element = await self.page.query_selector(self.selectors["pagination"]["current_page"])
            current_page = 1
            if current_page_element:
                current_page_text = await safe_get_text(current_page_element)
                try:
                    current_page = int(current_page_text)
                except ValueError:
                    current_page = 1
            
            # 총 페이지 수 계산 (페이지 번호 중 가장 큰 값)
            total_pages = 1
            for page_element in page_elements:
                page_text = await safe_get_text(page_element)
                try:
                    page_num = int(page_text)
                    total_pages = max(total_pages, page_num)
                except ValueError:
                    continue
            
            self.logger.info(f"페이지네이션 정보: 현재 {current_page}페이지 / 총 {total_pages}페이지")
            
            return {
                "has_pagination": True,
                "total_pages": total_pages,
                "current_page": current_page
            }
            
        except Exception as e:
            self.logger.warning(f"페이지네이션 정보 추출 실패: {e}")
            return {"has_pagination": False, "total_pages": 1, "current_page": 1}
    
    async def go_to_page(self, page_number: int) -> bool:
        """
        특정 페이지로 이동합니다.
        
        Args:
            page_number: 이동할 페이지 번호
            
        Returns:
            페이지 이동 성공 여부
        """
        try:
            # 페이지네이션 정보 확인
            pagination_info = await self.get_pagination_info()
            if not pagination_info["has_pagination"]:
                return True  # 페이지네이션이 없으면 성공으로 처리
            
            if page_number > pagination_info["total_pages"]:
                self.logger.warning(f"페이지 번호 범위 초과: {page_number} > {pagination_info['total_pages']}")
                return False
            
            # 현재 페이지가 이미 원하는 페이지인 경우
            if pagination_info["current_page"] == page_number:
                return True
            
            # 페이지 번호 클릭
            page_elements = await self.page.query_selector_all(self.selectors["pagination"]["page_numbers"])
            
            for page_element in page_elements:
                page_text = await safe_get_text(page_element)
                try:
                    if int(page_text) == page_number:
                        await page_element.click()
                        await safe_delay(1.0)  # 페이지 로딩 대기
                        await self.page.wait_for_load_state("networkidle")
                        
                        self.logger.info(f"페이지 {page_number}로 이동 완료")
                        return True
                except ValueError:
                    continue
            
            # 페이지 번호를 찾지 못한 경우, 다음 버튼으로 이동 시도
            if page_number > pagination_info["current_page"]:
                next_button = await self.page.query_selector(self.selectors["pagination"]["next_button"])
                if next_button:
                    await next_button.click()
                    await safe_delay(1.0)
                    await self.page.wait_for_load_state("networkidle")
                    
                    # 재귀적으로 다음 페이지 확인
                    return await self.go_to_page(page_number)
            
            self.logger.warning(f"페이지 {page_number}로 이동 실패")
            return False
            
        except Exception as e:
            self.logger.error(f"페이지 이동 실패 (페이지 {page_number}): {e}")
            return False 