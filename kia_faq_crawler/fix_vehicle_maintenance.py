#!/usr/bin/env python3
"""
차량 정비 카테고리 수정 스크립트 - 원시 데이터에서 10개 FAQ 복원
"""

import json
from datetime import datetime
from collections import Counter

def fix_vehicle_maintenance():
    # 수정된 FAQ 데이터 읽기
    with open('data/processed/kia_faq_fixed_20250731_100207.json', 'r', encoding='utf-8') as f:
        fixed_data = json.load(f)
    
    # 원시 데이터 읽기
    with open('data/raw/kia_faq_raw_20250731_095401.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print("=" * 60)
    print("차량 정비 카테고리 수정 시작")
    print("=" * 60)
    
    # 현재 상태 확인
    categories = [item['category'] for item in fixed_data['data']]
    category_counts = Counter(categories)
    
    print(f"현재 차량 정비: {category_counts.get('차량 정비', 0)}개")
    
    # 원시 데이터에서 차량 정비 카테고리 찾기
    vehicle_maintenance_items = []
    for item in raw_data:
        if item['category'] == '차량 정비':
            vehicle_maintenance_items.append(item)
    
    print(f"원시 데이터에서 차량 정비: {len(vehicle_maintenance_items)}개")
    
    # 기존 차량 정비 아이템 제거
    fixed_data['data'] = [item for item in fixed_data['data'] if item['category'] != '차량 정비']
    
    # 원시 데이터의 차량 정비 아이템들을 추가
    for i, item in enumerate(vehicle_maintenance_items):
        # 고유 ID 부여
        item['category_id'] = 'category_4'
        item['question_id'] = f'q_3_{i}'
        item['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 수정된 데이터에 추가
        fixed_data['data'].append(item)
    
    # 메타데이터 업데이트
    fixed_data['metadata']['total_items'] = len(fixed_data['data'])
    fixed_data['metadata']['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 수정된 데이터 저장
    final_filename = f"data/processed/kia_faq_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(final_filename, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    
    # 수정된 카테고리별 분포 확인
    final_categories = [item['category'] for item in fixed_data['data']]
    final_category_counts = Counter(final_categories)
    
    print(f"\n수정된 카테고리별 분포:")
    for category, count in sorted(final_category_counts.items()):
        print(f"• {category}: {count}개")
    
    print(f"\n✅ 차량 정비 카테고리 수정 완료!")
    print(f"📁 저장된 파일: {final_filename}")
    print(f"📊 총 FAQ 수: {len(fixed_data['data'])}개")
    print(f"📊 총 카테고리 수: {len(final_category_counts)}개")
    
    # CSV 파일도 생성
    import csv
    csv_filename = final_filename.replace('.json', '.csv')
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['category', 'category_id', 'question', 'answer', 'question_id', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in fixed_data['data']:
            writer.writerow(item)
    
    print(f"📁 CSV 파일 저장: {csv_filename}")
    
    # 최종 리포트 생성
    report_filename = final_filename.replace('.json', '_report.txt')
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("기아자동차 FAQ 크롤링 리포트 (최종 수정됨)\n")
        f.write("=" * 60 + "\n")
        f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"총 수집 항목: {len(fixed_data['data'])}개\n")
        f.write(f"총 카테고리: {len(final_category_counts)}개\n")
        
        # 평균 길이 계산
        avg_question_length = sum(len(item['question']) for item in fixed_data['data']) / len(fixed_data['data'])
        avg_answer_length = sum(len(item['answer']) for item in fixed_data['data']) / len(fixed_data['data'])
        
        f.write(f"평균 질문 길이: {avg_question_length:.2f}자\n")
        f.write(f"평균 답변 길이: {avg_answer_length:.2f}자\n\n")
        
        f.write("카테고리별 분포:\n")
        f.write("-" * 30 + "\n")
        for category, count in sorted(final_category_counts.items()):
            f.write(f"{category}: {count}개\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"📁 리포트 저장: {report_filename}")
    
    return final_filename

if __name__ == "__main__":
    fix_vehicle_maintenance() 