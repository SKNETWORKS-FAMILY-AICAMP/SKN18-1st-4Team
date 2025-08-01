"""
기아자동차 FAQ 파일 관리 클래스
"""

import json
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .utils import format_timestamp


class FileManager:
    """
    FAQ 데이터 파일 저장 및 관리 클래스
    """
    
    def __init__(self, output_dir: str = "data/processed", 
                 raw_dir: str = "data/raw", 
                 reports_dir: str = "data/reports",
                 logger: Optional[logging.Logger] = None):
        """
        FileManager 초기화
        
        Args:
            output_dir: 처리된 데이터 저장 디렉토리
            raw_dir: 원시 데이터 저장 디렉토리
            reports_dir: 리포트 저장 디렉토리
            logger: 로거 객체
        """
        self.output_dir = output_dir
        self.raw_dir = raw_dir
        self.reports_dir = reports_dir
        self.logger = logger or logging.getLogger(__name__)
        
        # 디렉토리 생성
        self._ensure_directories()
    
    def _ensure_directories(self):
        """필요한 디렉토리들을 생성합니다."""
        directories = [self.output_dir, self.raw_dir, self.reports_dir]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                self.logger.info(f"디렉토리 생성: {directory}")
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        데이터를 JSON 파일로 저장합니다.
        
        Args:
            data: 저장할 데이터
            filename: 파일명 (None이면 자동 생성)
            
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kia_faq_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # 데이터에 메타데이터 추가
            output_data = {
                "metadata": {
                    "created_at": format_timestamp(),
                    "total_items": len(data),
                    "source": "기아자동차 FAQ",
                    "version": "1.0"
                },
                "data": data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"JSON 파일 저장 완료: {filepath} ({len(data)}개 항목)")
            return filepath
            
        except Exception as e:
            self.logger.error(f"JSON 파일 저장 실패: {e}")
            raise
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        데이터를 CSV 파일로 저장합니다.
        
        Args:
            data: 저장할 데이터
            filename: 파일명 (None이면 자동 생성)
            
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kia_faq_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            
            # 컬럼 순서 정리
            columns_order = ['category', 'question', 'answer', 'category_id', 'question_id']
            existing_columns = [col for col in columns_order if col in df.columns]
            other_columns = [col for col in df.columns if col not in columns_order]
            
            df = df[existing_columns + other_columns]
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            self.logger.info(f"CSV 파일 저장 완료: {filepath} ({len(data)}개 항목)")
            return filepath
            
        except Exception as e:
            self.logger.error(f"CSV 파일 저장 실패: {e}")
            raise
    
    def save_raw_data(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        원시 데이터를 저장합니다.
        
        Args:
            data: 저장할 원시 데이터
            filename: 파일명 (None이면 자동 생성)
            
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kia_faq_raw_{timestamp}.json"
        
        filepath = os.path.join(self.raw_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"원시 데이터 저장 완료: {filepath} ({len(data)}개 항목)")
            return filepath
            
        except Exception as e:
            self.logger.error(f"원시 데이터 저장 실패: {e}")
            raise
    
    def generate_report(self, stats: Dict[str, Any], filename: str = None) -> str:
        """
        통계 리포트를 생성합니다.
        
        Args:
            stats: 통계 데이터
            filename: 파일명 (None이면 자동 생성)
            
        Returns:
            생성된 리포트 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kia_faq_report_{timestamp}.txt"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("기아자동차 FAQ 크롤링 리포트\n")
                f.write("=" * 60 + "\n")
                f.write(f"생성일시: {format_timestamp()}\n")
                f.write(f"총 수집 항목: {stats.get('total_items', 0)}개\n")
                f.write(f"총 카테고리: {stats.get('total_categories', 0)}개\n")
                f.write(f"평균 질문 길이: {stats.get('avg_question_length', 0)}자\n")
                f.write(f"평균 답변 길이: {stats.get('avg_answer_length', 0)}자\n")
                f.write(f"링크 포함 항목: {stats.get('items_with_links', 0)}개\n")
                f.write("\n")
                
                # 카테고리별 분포
                f.write("카테고리별 분포:\n")
                f.write("-" * 30 + "\n")
                category_dist = stats.get('category_distribution', {})
                for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"{category}: {count}개\n")
                
                f.write("\n")
                f.write("=" * 60 + "\n")
            
            self.logger.info(f"리포트 생성 완료: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"리포트 생성 실패: {e}")
            raise
    
    def load_from_json(self, filepath: str) -> List[Dict[str, Any]]:
        """
        JSON 파일에서 데이터를 로드합니다.
        
        Args:
            filepath: 로드할 파일 경로
            
        Returns:
            로드된 데이터
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 메타데이터가 있는 경우 데이터 부분만 반환
            if isinstance(data, dict) and 'data' in data:
                return data['data']
            else:
                return data
                
        except Exception as e:
            self.logger.error(f"JSON 파일 로드 실패: {e}")
            raise
    
    def load_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """
        CSV 파일에서 데이터를 로드합니다.
        
        Args:
            filepath: 로드할 파일 경로
            
        Returns:
            로드된 데이터
        """
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            return df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"CSV 파일 로드 실패: {e}")
            raise
    
    def get_latest_files(self, file_pattern: str = "kia_faq_*.json") -> List[str]:
        """
        최신 파일들을 찾습니다.
        
        Args:
            file_pattern: 파일 패턴
            
        Returns:
            최신 파일 경로 리스트
        """
        import glob
        
        pattern = os.path.join(self.output_dir, file_pattern)
        files = glob.glob(pattern)
        
        # 수정 시간 기준으로 정렬
        files.sort(key=os.path.getmtime, reverse=True)
        
        return files
    
    def backup_files(self, backup_dir: str = "backup") -> str:
        """
        현재 파일들을 백업합니다.
        
        Args:
            backup_dir: 백업 디렉토리
            
        Returns:
            백업 디렉토리 경로
        """
        import shutil
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"kia_faq_backup_{timestamp}")
        
        try:
            if not os.path.exists(backup_path):
                os.makedirs(backup_path, exist_ok=True)
            
            # 각 디렉토리 복사
            for source_dir in [self.output_dir, self.raw_dir, self.reports_dir]:
                if os.path.exists(source_dir):
                    dest_dir = os.path.join(backup_path, os.path.basename(source_dir))
                    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
            
            self.logger.info(f"백업 완료: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"백업 실패: {e}")
            raise 