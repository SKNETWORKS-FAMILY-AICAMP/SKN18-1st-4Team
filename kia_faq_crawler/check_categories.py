#!/usr/bin/env python3
"""
카테고리별 분포 확인 스크립트
"""

import json
from collections import Counter

def check_categories():
    # JSON 파일 읽기
    with open('data/processed/kia_faq_20250731_094409.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 카테고리별 개수 세기
    categories = [item['category'] for item in data['data']]
    category_counts = Counter(categories)
    
    print("=" * 50)
    print("카테고리별 분포 확인")
    print("=" * 50)
    
    print(f"총 FAQ 수: {len(data['data'])}")
    print(f"총 카테고리 수: {len(category_counts)}")
    print()
    
    print("카테고리별 분포:")
    print("-" * 30)
    for category, count in sorted(category_counts.items()):
        print(f"{category}: {count}개")
    
    print()
    print("카테고리 목록:")
    print("-" * 30)
    for category in sorted(category_counts.keys()):
        print(f"• {category}")
    
    # 사용자가 제공한 정보와 비교
    print()
    print("=" * 50)
    print("사용자 제공 정보와 비교")
    print("=" * 50)
    
    user_categories = ["TOP 10", "전체", "차량구매", "차량정비", "기아멤버스", "홈페이지", "PRV", "기타"]
    
    print("사용자 제공 카테고리:")
    for cat in user_categories:
        count = category_counts.get(cat, 0)
        print(f"• {cat}: {count}개")
    
    # 누락된 카테고리 확인
    print()
    print("누락된 카테고리:")
    missing = []
    for cat in user_categories:
        if cat not in category_counts:
            missing.append(cat)
    
    if missing:
        for cat in missing:
            print(f"❌ {cat}")
    else:
        print("✅ 모든 카테고리가 수집되었습니다.")

if __name__ == "__main__":
    check_categories() 