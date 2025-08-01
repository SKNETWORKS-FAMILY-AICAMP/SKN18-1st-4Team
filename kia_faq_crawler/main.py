#!/usr/bin/env python3
"""
기아자동차 FAQ 크롤링 메인 실행 파일
"""

import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.crawler import KiaFAQCrawler
from src.data_processor import DataProcessor
from src.file_manager import FileManager
from src.utils import setup_logging
from config.settings import (
    WEBSITE_URL, SELECTORS, BROWSER_CONFIG, 
    CRAWLING_CONFIG, FILE_CONFIG, LOGGING_CONFIG
)


async def main():
    """
    메인 실행 함수
    """
    print("=" * 60)
    print("기아자동차 FAQ 크롤링 시스템")
    print("=" * 60)
    
    # 로깅 설정
    logger = setup_logging(LOGGING_CONFIG)
    logger.info("기아자동차 FAQ 크롤링 시스템 시작")
    
    try:
        # 1. 크롤러 초기화
        logger.info("크롤러 초기화 중...")
        crawler = KiaFAQCrawler(
            website_url=WEBSITE_URL,
            selectors=SELECTORS,
            browser_config=BROWSER_CONFIG,
            crawling_config=CRAWLING_CONFIG,
            logger=logger
        )
        
        # 2. 데이터 처리기 초기화
        logger.info("데이터 처리기 초기화 중...")
        data_processor = DataProcessor(logger=logger)
        
        # 3. 파일 관리자 초기화
        logger.info("파일 관리자 초기화 중...")
        file_manager = FileManager(
            output_dir=FILE_CONFIG["output_dir"],
            raw_dir=FILE_CONFIG["raw_dir"],
            reports_dir=FILE_CONFIG["reports_dir"],
            logger=logger
        )
        
        # 4. 크롤링 실행
        logger.info("크롤링 시작...")
        raw_data = await crawler.run()
        
        if not raw_data:
            logger.error("크롤링 결과가 없습니다.")
            return
        
        # 5. 원시 데이터 저장
        logger.info("원시 데이터 저장 중...")
        raw_file_path = file_manager.save_raw_data(raw_data)
        logger.info(f"원시 데이터 저장 완료: {raw_file_path}")
        
        # 6. 데이터 처리
        logger.info("데이터 처리 중...")
        processed_data = data_processor.process_data(raw_data)
        
        if not processed_data:
            logger.error("처리된 데이터가 없습니다.")
            return
        
        # 7. 처리된 데이터 저장
        logger.info("처리된 데이터 저장 중...")
        
        # JSON 파일 저장
        json_file_path = file_manager.save_to_json(processed_data)
        logger.info(f"JSON 파일 저장 완료: {json_file_path}")
        
        # CSV 파일 저장
        csv_file_path = file_manager.save_to_csv(processed_data)
        logger.info(f"CSV 파일 저장 완료: {csv_file_path}")
        
        # 8. 통계 리포트 생성
        logger.info("통계 리포트 생성 중...")
        stats = data_processor.get_summary_stats()
        report_file_path = file_manager.generate_report(stats)
        logger.info(f"리포트 생성 완료: {report_file_path}")
        
        # 9. 결과 출력
        print("\n" + "=" * 60)
        print("크롤링 완료!")
        print("=" * 60)
        
        summary = crawler.get_summary()
        print(f"📊 수집 결과:")
        print(f"   • 총 카테고리: {summary['total_categories']}개")
        print(f"   • 총 FAQ: {summary['total_faqs']}개")
        print(f"   • 카테고리 목록: {', '.join(summary['categories'])}")
        
        print(f"\n📁 저장된 파일:")
        print(f"   • 원시 데이터: {raw_file_path}")
        print(f"   • JSON 파일: {json_file_path}")
        print(f"   • CSV 파일: {csv_file_path}")
        print(f"   • 리포트: {report_file_path}")
        
        print(f"\n📈 데이터 통계:")
        print(f"   • 처리된 항목: {stats['total_items']}개")
        print(f"   • 카테고리 수: {stats['total_categories']}개")
        print(f"   • 평균 질문 길이: {stats['avg_question_length']}자")
        print(f"   • 평균 답변 길이: {stats['avg_answer_length']}자")
        
        print(f"\n📋 카테고리별 분포:")
        for category, count in stats['category_distribution'].items():
            print(f"   • {category}: {count}개")
        
        logger.info("기아자동차 FAQ 크롤링 시스템 완료")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
        print("\n⚠️  크롤링이 중단되었습니다.")
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}")
        print(f"\n❌ 오류 발생: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        # asyncio 이벤트 루프 실행
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  프로그램이 중단되었습니다.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1) 