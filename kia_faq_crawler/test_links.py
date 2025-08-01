#!/usr/bin/env python3
"""
링크 수집 기능 테스트 스크립트
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.crawler import KiaFAQCrawler
from src.data_processor import DataProcessor
from src.file_manager import FileManager
import logging

async def test_link_crawling():
    """링크 수집 기능을 테스트합니다."""
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("링크 수집 테스트 시작...")
        
        # 크롤러 초기화
        crawler = KiaFAQCrawler(logger=logger)
        
        # 첫 번째 카테고리만 테스트 (빠른 테스트를 위해)
        await crawler.setup_browser()
        await crawler.navigate_to_page()
        
        # 카테고리 목록 가져오기
        categories = await crawler.get_categories()
        if not categories:
            logger.error("카테고리를 찾을 수 없습니다.")
            return
        
        logger.info(f"발견된 카테고리: {len(categories)}개")
        
        # 첫 번째 카테고리만 테스트
        test_category = categories[0]
        logger.info(f"테스트 카테고리: {test_category['category_name']}")
        
        # FAQ 수집
        faqs = await crawler.get_faqs_by_category(test_category)
        
        # 링크가 있는 FAQ 찾기
        faqs_with_links = [faq for faq in faqs if faq.get('links')]
        
        logger.info(f"총 FAQ 수: {len(faqs)}개")
        logger.info(f"링크 포함 FAQ 수: {len(faqs_with_links)}개")
        
        # 링크가 있는 FAQ 예시 출력
        if faqs_with_links:
            logger.info("링크가 포함된 FAQ 예시:")
            for i, faq in enumerate(faqs_with_links[:3]):  # 처음 3개만
                logger.info(f"\n--- FAQ {i+1} ---")
                logger.info(f"질문: {faq['question'][:100]}...")
                logger.info(f"답변: {faq['answer'][:100]}...")
                logger.info(f"링크 수: {len(faq['links'])}개")
                for j, link in enumerate(faq['links']):
                    logger.info(f"  링크 {j+1}: {link['text']} -> {link['url']}")
        else:
            logger.info("링크가 포함된 FAQ가 없습니다.")
        
        # 데이터 처리 테스트
        processor = DataProcessor(logger=logger)
        processed_data = processor.process_data(faqs)
        
        # 파일 저장 테스트
        file_manager = FileManager(logger=logger)
        
        # JSON 저장
        json_path = file_manager.save_to_json(processed_data, "test_links.json")
        logger.info(f"JSON 저장 완료: {json_path}")
        
        # CSV 저장
        csv_path = file_manager.save_to_csv(processed_data, "test_links.csv")
        logger.info(f"CSV 저장 완료: {csv_path}")
        
        # 통계 리포트 생성
        stats = processor.get_summary_stats()
        report_path = file_manager.generate_report(stats, "test_links_report.txt")
        logger.info(f"리포트 생성 완료: {report_path}")
        
        logger.info("링크 수집 테스트 완료!")
        
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
        raise
    
    finally:
        # 브라우저 정리
        if hasattr(crawler, 'cleanup'):
            await crawler.cleanup()

if __name__ == "__main__":
    asyncio.run(test_link_crawling()) 