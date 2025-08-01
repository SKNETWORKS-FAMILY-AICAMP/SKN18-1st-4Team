"""
기아자동차 FAQ 데이터 처리 클래스
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from collections import defaultdict
import logging
from .utils import clean_text, generate_id, extract_category_from_text


class DataProcessor:
    """
    FAQ 데이터를 처리하고 정제하는 클래스
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        DataProcessor 초기화
        
        Args:
            logger: 로거 객체
        """
        self.logger = logger or logging.getLogger(__name__)
        self.processed_data = []
        self.category_stats = defaultdict(int)
    
    def clean_text_data(self, text: str) -> str:
        """
        텍스트 데이터를 정제합니다.
        
        Args:
            text: 정제할 텍스트
            
        Returns:
            정제된 텍스트
        """
        if not text:
            return ""
        
        # 기본 정제
        cleaned = clean_text(text)
        
        # HTML 태그 제거 (간단한 패턴)
        import re
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # 연속된 공백 제거
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def format_links_for_csv(self, links: List[Dict[str, str]]) -> str:
        """
        링크 정보를 CSV용 텍스트로 변환합니다.
        
        Args:
            links: 링크 정보 리스트
            
        Returns:
            CSV용 링크 텍스트
        """
        if not links:
            return ""
        
        link_texts = []
        for link in links:
            text = link.get('text', '')
            url = link.get('url', '')
            if text and url:
                link_texts.append(f"{text} ({url})")
        
        return " | ".join(link_texts)
    
    def remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        중복 데이터를 제거합니다.
        
        Args:
            data: 중복을 제거할 데이터 리스트
            
        Returns:
            중복이 제거된 데이터 리스트
        """
        if not data:
            return []
        
        # 질문과 답변을 기준으로 중복 제거
        seen = set()
        unique_data = []
        
        for item in data:
            question = self.clean_text_data(item.get('question', ''))
            answer = self.clean_text_data(item.get('answer', ''))
            
            # 질문과 답변의 조합으로 중복 체크
            key = f"{question[:100]}_{answer[:100]}"
            
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        self.logger.info(f"중복 제거: {len(data)} -> {len(unique_data)}")
        return unique_data
    
    def categorize_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        데이터를 카테고리별로 분류합니다.
        
        Args:
            data: 분류할 데이터 리스트
            
        Returns:
            카테고리가 추가된 데이터 리스트
        """
        categorized_data = []
        
        for item in data:
            question = item.get('question', '')
            answer = item.get('answer', '')
            
            # 기존 카테고리가 있으면 유지, 없으면 추출
            if 'category' not in item or not item['category']:
                category = extract_category_from_text(question + ' ' + answer)
                item['category'] = category
            
            # 카테고리 통계 업데이트
            self.category_stats[item['category']] += 1
            
            # ID 생성
            if 'question_id' not in item:
                item['question_id'] = generate_id(question)
            
            if 'category_id' not in item:
                item['category_id'] = generate_id(item['category'])
            
            categorized_data.append(item)
        
        return categorized_data
    
    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        데이터 유효성을 검증합니다.
        
        Args:
            data: 검증할 데이터 리스트
            
        Returns:
            유효한 데이터 리스트
        """
        valid_data = []
        
        for item in data:
            question = self.clean_text_data(item.get('question', ''))
            answer = self.clean_text_data(item.get('answer', ''))
            
            # 최소 길이 검증
            if len(question) < 5:
                self.logger.warning(f"질문이 너무 짧습니다: {question}")
                continue
            
            if len(answer) < 10:
                self.logger.warning(f"답변이 너무 짧습니다: {answer}")
                continue
            
            # 필수 필드 검증
            if not question or not answer:
                self.logger.warning("질문 또는 답변이 비어있습니다")
                continue
            
            item['question'] = question
            item['answer'] = answer
            valid_data.append(item)
        
        self.logger.info(f"데이터 검증: {len(data)} -> {len(valid_data)}")
        return valid_data
    
    def process_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        원시 데이터를 처리합니다.
        
        Args:
            raw_data: 처리할 원시 데이터
            
        Returns:
            처리된 데이터
        """
        self.logger.info(f"데이터 처리 시작: {len(raw_data)}개 항목")
        
        # 1. 텍스트 정제
        cleaned_data = []
        for item in raw_data:
            cleaned_item = item.copy()
            cleaned_item['question'] = self.clean_text_data(item.get('question', ''))
            cleaned_item['answer'] = self.clean_text_data(item.get('answer', ''))
            
            # 링크 정보 처리
            links = item.get('links', [])
            if links:
                # CSV용 링크 텍스트 추가
                cleaned_item['links_text'] = self.format_links_for_csv(links)
                # 원본 링크 정보 유지
                cleaned_item['links'] = links
            else:
                cleaned_item['links_text'] = ""
                cleaned_item['links'] = []
            
            cleaned_data.append(cleaned_item)
        
        # 2. 중복 제거
        unique_data = self.remove_duplicates(cleaned_data)
        
        # 3. 카테고리 분류
        categorized_data = self.categorize_data(unique_data)
        
        # 4. 데이터 검증
        validated_data = self.validate_data(categorized_data)
        
        # 5. 최종 데이터 저장
        self.processed_data = validated_data
        
        self.logger.info(f"데이터 처리 완료: {len(self.processed_data)}개 항목")
        return self.processed_data
    
    def get_category_stats(self) -> Dict[str, int]:
        """
        카테고리별 통계를 반환합니다.
        
        Returns:
            카테고리별 개수 딕셔너리
        """
        return dict(self.category_stats)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        전체 통계 요약을 반환합니다.
        
        Returns:
            통계 요약 딕셔너리
        """
        if not self.processed_data:
            return {
                'total_items': 0,
                'total_categories': 0,
                'avg_question_length': 0,
                'avg_answer_length': 0
            }
        
        total_items = len(self.processed_data)
        total_categories = len(self.category_stats)
        
        question_lengths = [len(item.get('question', '')) for item in self.processed_data]
        answer_lengths = [len(item.get('answer', '')) for item in self.processed_data]
        
        avg_question_length = sum(question_lengths) / len(question_lengths) if question_lengths else 0
        avg_answer_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
        
        # 링크가 있는 항목 수 계산
        items_with_links = sum(1 for item in self.processed_data if item.get('links'))
        
        return {
            'total_items': total_items,
            'total_categories': total_categories,
            'avg_question_length': round(avg_question_length, 2),
            'avg_answer_length': round(avg_answer_length, 2),
            'items_with_links': items_with_links,
            'category_distribution': dict(self.category_stats)
        }
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        처리된 데이터를 pandas DataFrame으로 변환합니다.
        
        Returns:
            데이터프레임
        """
        if not self.processed_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.processed_data)
        
        # 컬럼 순서 정리
        columns_order = ['category', 'question', 'answer', 'links_text', 'category_id', 'question_id']
        existing_columns = [col for col in columns_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in columns_order]
        
        df = df[existing_columns + other_columns]
        
        return df 