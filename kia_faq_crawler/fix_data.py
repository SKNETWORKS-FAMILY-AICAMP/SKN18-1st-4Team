#!/usr/bin/env python3
"""
데이터 수정 스크립트 - 기타 카테고리 통합 및 차량 정비 카테고리 수정
"""

import json
from datetime import datetime
from collections import Counter

def fix_faq_data():
    # 메인 FAQ 데이터 읽기
    with open('data/processed/kia_faq_20250731_095401.json', 'r', encoding='utf-8') as f:
        main_data = json.load(f)
    
    # 기타 카테고리 데이터 읽기
    with open('data/processed/others_faq_20250731_095727.json', 'r', encoding='utf-8') as f:
        others_data = json.load(f)
    
    print("=" * 60)
    print("데이터 수정 시작")
    print("=" * 60)
    
    # 현재 상태 확인
    print(f"메인 데이터: {len(main_data['data'])}개")
    print(f"기타 카테고리: {len(others_data['data'])}개")
    
    # 카테고리별 분포 확인
    categories = [item['category'] for item in main_data['data']]
    category_counts = Counter(categories)
    
    print("\n현재 카테고리별 분포:")
    for category, count in sorted(category_counts.items()):
        print(f"• {category}: {count}개")
    
    # 기타 카테고리 데이터를 메인 데이터에 추가
    print(f"\n기타 카테고리 {len(others_data['data'])}개 추가 중...")
    
    for i, others_item in enumerate(others_data['data']):
        # 기타 카테고리 아이템에 고유 ID 부여
        others_item['category_id'] = f"category_8"
        others_item['question_id'] = f"q_7_{i}"
        others_item['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 메인 데이터에 추가
        main_data['data'].append(others_item)
    
    # 메타데이터 업데이트
    main_data['metadata']['total_items'] = len(main_data['data'])
    main_data['metadata']['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 수정된 데이터 저장
    fixed_filename = f"data/processed/kia_faq_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fixed_filename, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)
    
    # 수정된 카테고리별 분포 확인
    fixed_categories = [item['category'] for item in main_data['data']]
    fixed_category_counts = Counter(fixed_categories)
    
    print(f"\n수정된 카테고리별 분포:")
    for category, count in sorted(fixed_category_counts.items()):
        print(f"• {category}: {count}개")
    
    print(f"\n✅ 데이터 수정 완료!")
    print(f"📁 저장된 파일: {fixed_filename}")
    print(f"📊 총 FAQ 수: {len(main_data['data'])}개")
    print(f"📊 총 카테고리 수: {len(fixed_category_counts)}개")
    
    # CSV 파일도 생성
    import csv
    csv_filename = fixed_filename.replace('.json', '.csv')
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['category', 'category_id', 'question', 'answer', 'question_id', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in main_data['data']:
            writer.writerow(item)
    
    print(f"📁 CSV 파일 저장: {csv_filename}")
    
    # 리포트 생성
    report_filename = fixed_filename.replace('.json', '_report.txt')
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("기아자동차 FAQ 크롤링 리포트 (수정됨)\n")
        f.write("=" * 60 + "\n")
        f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"총 수집 항목: {len(main_data['data'])}개\n")
        f.write(f"총 카테고리: {len(fixed_category_counts)}개\n")
        
        # 평균 길이 계산
        avg_question_length = sum(len(item['question']) for item in main_data['data']) / len(main_data['data'])
        avg_answer_length = sum(len(item['answer']) for item in main_data['data']) / len(main_data['data'])
        
        f.write(f"평균 질문 길이: {avg_question_length:.2f}자\n")
        f.write(f"평균 답변 길이: {avg_answer_length:.2f}자\n\n")
        
        f.write("카테고리별 분포:\n")
        f.write("-" * 30 + "\n")
        for category, count in sorted(fixed_category_counts.items()):
            f.write(f"{category}: {count}개\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"📁 리포트 저장: {report_filename}")
    
    return fixed_filename

if __name__ == "__main__":
    fix_faq_data() 