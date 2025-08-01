#!/usr/bin/env python3
"""
기아자동차 FAQ 크롤러 (링크 수집 포함) - 메인 실행 스크립트
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.crawler import KiaFAQCrawler
from src.data_processor import DataProcessor
from src.file_manager import FileManager
from config.settings import SELECTORS, BROWSER_CONFIG, CRAWLING_CONFIG, FILE_CONFIG
import logging
from datetime import datetime


async def main():
    """메인 실행 함수"""
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(FILE_CONFIG['logs_dir'] + '/kia_faq_crawler.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info("기아자동차 FAQ 크롤링 시작 (링크 수집 포함)")
        logger.info("=" * 60)
        
        # 1. 크롤러 초기화
        crawler = KiaFAQCrawler(
            selectors=SELECTORS,
            browser_config=BROWSER_CONFIG,
            crawling_config=CRAWLING_CONFIG,
            logger=logger
        )
        
        # 2. 크롤링 실행
        logger.info("크롤링 시작...")
        raw_data = await crawler.run()
        
        if not raw_data:
            logger.error("크롤링된 데이터가 없습니다.")
            return
        
        logger.info(f"크롤링 완료: {len(raw_data)}개 FAQ 수집")
        
        # 3. 데이터 처리
        logger.info("데이터 처리 시작...")
        processor = DataProcessor(logger=logger)
        processed_data = processor.process_data(raw_data)
        
        # 4. 통계 정보
        stats = processor.get_summary_stats()
        logger.info(f"처리 완료: {stats['total_items']}개 FAQ, {stats['total_categories']}개 카테고리")
        logger.info(f"링크 포함 항목: {stats['items_with_links']}개")
        
        # 5. 파일 저장
        logger.info("파일 저장 시작...")
        file_manager = FileManager(
            output_dir=FILE_CONFIG['output_dir'],
            raw_dir=FILE_CONFIG['raw_dir'],
            reports_dir=FILE_CONFIG['reports_dir'],
            logger=logger
        )
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 원시 데이터 저장
        raw_filename = f"kia_faq_raw_{timestamp}.json"
        raw_path = file_manager.save_raw_data(raw_data, raw_filename)
        logger.info(f"원시 데이터 저장: {raw_path}")
        
        # 처리된 데이터 저장 (JSON)
        json_filename = f"Final__kia_faq_{timestamp}.json"
        json_path = file_manager.save_to_json(processed_data, json_filename)
        logger.info(f"JSON 저장: {json_path}")
        
        # 처리된 데이터 저장 (CSV)
        csv_filename = f"Final__kia_faq_{timestamp}.csv"
        csv_path = file_manager.save_to_csv(processed_data, csv_filename)
        logger.info(f"CSV 저장: {csv_path}")
        
        # 리포트 생성
        report_filename = f"Final__kia_faq_report_{timestamp}.txt"
        report_path = file_manager.generate_report(stats, report_filename)
        logger.info(f"리포트 생성: {report_path}")
        
        # 6. 최종 요약
        logger.info("=" * 60)
        logger.info("크롤링 완료 요약")
        logger.info("=" * 60)
        logger.info(f"총 FAQ 수: {stats['total_items']}개")
        logger.info(f"총 카테고리: {stats['total_categories']}개")
        logger.info(f"링크 포함 항목: {stats['items_with_links']}개")
        logger.info(f"평균 질문 길이: {stats['avg_question_length']}자")
        logger.info(f"평균 답변 길이: {stats['avg_answer_length']}자")
        logger.info(f"저장된 파일:")
        logger.info(f"  - 원시 데이터: {raw_path}")
        logger.info(f"  - JSON: {json_path}")
        logger.info(f"  - CSV: {csv_path}")
        logger.info(f"  - 리포트: {report_path}")
        
        # 카테고리별 분포 출력
        logger.info("\n카테고리별 분포:")
        for category, count in sorted(stats['category_distribution'].items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {category}: {count}개")
        
        logger.info("=" * 60)
        logger.info("모든 작업이 성공적으로 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"크롤링 실행 중 오류 발생: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 