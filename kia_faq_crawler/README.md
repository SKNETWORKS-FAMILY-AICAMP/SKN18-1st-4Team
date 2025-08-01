# 기아자동차 FAQ 크롤링 시스템

기아자동차 공식 FAQ 페이지에서 카테고리별 질문과 답변을 자동으로 수집하는 Python 기반 웹 크롤링 시스템입니다.

## 🎯 프로젝트 개요

- **대상 웹사이트**: https://www.kia.com/kr/customer-service/center/faq
- **기술 스택**: Python 3.8+, Playwright, Pandas
- **주요 기능**: 카테고리별 FAQ 자동 수집, 데이터 정제, CSV/JSON 저장

## 📋 주요 기능

### ✅ 구현된 기능
- [x] Playwright 기반 웹 브라우저 자동화
- [x] 카테고리별 FAQ 자동 수집
- [x] 질문-답변 쌍 정확한 매칭
- [x] 데이터 정제 및 중복 제거
- [x] CSV/JSON 형태로 데이터 저장
- [x] 통계 리포트 자동 생성
- [x] 상세한 로깅 시스템
- [x] 에러 처리 및 재시도 메커니즘

### 🔧 기술적 특징
- **비동기 처리**: asyncio 기반 고성능 크롤링
- **모듈화 설계**: 확장 가능한 클래스 기반 구조
- **설정 관리**: 외부 설정 파일을 통한 유연한 관리
- **데이터 검증**: 자동 데이터 품질 검증 및 정제

## 🏗️ 프로젝트 구조

```
kia_faq_crawler/
├── src/                    # 소스 코드
│   ├── __init__.py
│   ├── crawler.py          # 메인 크롤러 클래스
│   ├── data_processor.py   # 데이터 처리 클래스
│   ├── file_manager.py     # 파일 관리 클래스
│   └── utils.py           # 유틸리티 함수
├── config/                 # 설정 파일
│   └── settings.py        # 프로젝트 설정
├── data/                   # 데이터 저장소
│   ├── raw/               # 원시 데이터
│   ├── processed/         # 처리된 데이터
│   └── reports/           # 리포트 파일
├── logs/                   # 로그 파일
├── tests/                  # 테스트 코드
├── requirements.txt        # 의존성 패키지
├── main.py                # 실행 파일
└── README.md              # 프로젝트 문서
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd kia_faq_crawler

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치

```bash
# 필요한 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 3. 실행

```bash
# 메인 프로그램 실행
python main.py
```

## 📊 출력 결과

### 생성되는 파일들
- **원시 데이터**: `data/raw/kia_faq_raw_YYYYMMDD_HHMMSS.json`
- **JSON 파일**: `data/processed/kia_faq_YYYYMMDD_HHMMSS.json`
- **CSV 파일**: `data/processed/kia_faq_YYYYMMDD_HHMMSS.csv`
- **리포트**: `data/reports/kia_faq_report_YYYYMMDD_HHMMSS.txt`
- **로그**: `logs/kia_faq_crawler.log`

### 데이터 구조
```json
{
  "category": "카테고리명",
  "question": "질문 내용",
  "answer": "답변 내용",
  "category_id": "카테고리 ID",
  "question_id": "질문 ID",
  "created_at": "수집 시간"
}
```

## ⚙️ 설정

### config/settings.py
주요 설정 항목들을 수정할 수 있습니다:

```python
# 웹사이트 설정
WEBSITE_URL = "https://www.kia.com/kr/customer-service/center/faq"

# 셀렉터 설정
SELECTORS = {
    "category": "span.name",
    "question": "span.cmp-accordion__title",
    "answer": "div[id^='container-'] > div > p:first-of-type"
}

# 브라우저 설정
BROWSER_CONFIG = {
    "headless": True,      # 헤드리스 모드
    "slow_mo": 100,        # 동작 지연 (ms)
    "timeout": 30000       # 타임아웃 (ms)
}
```

## 🔍 사용법

### 기본 실행
```bash
python main.py
```

### 프로그래밍 방식 사용
```python
import asyncio
from src.crawler import KiaFAQCrawler
from src.data_processor import DataProcessor
from src.file_manager import FileManager

async def custom_crawling():
    # 크롤러 초기화
    crawler = KiaFAQCrawler()
    
    # 크롤링 실행
    raw_data = await crawler.run()
    
    # 데이터 처리
    processor = DataProcessor()
    processed_data = processor.process_data(raw_data)
    
    # 파일 저장
    file_manager = FileManager()
    file_manager.save_to_json(processed_data)
    file_manager.save_to_csv(processed_data)

# 실행
asyncio.run(custom_crawling())
```

## 📈 성능 지표

### 목표 성능
- **크롤링 성공률**: 90% 이상
- **평균 실행 시간**: 10분 이하
- **메모리 사용량**: 1GB 이하
- **데이터 정확도**: 95% 이상

### 모니터링
- 실시간 진행 상황 표시
- 상세한 로그 기록
- 에러 발생 시 자동 재시도
- 성능 통계 리포트 생성

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. Playwright 설치 오류
```bash
# 브라우저 재설치
playwright install --force chromium
```

#### 2. 네트워크 타임아웃
```python
# config/settings.py에서 타임아웃 증가
BROWSER_CONFIG = {
    "timeout": 60000  # 60초로 증가
}
```

#### 3. 셀렉터 변경
웹사이트 구조가 변경된 경우 `config/settings.py`의 `SELECTORS`를 업데이트하세요.

### 로그 확인
```bash
# 로그 파일 확인
tail -f logs/kia_faq_crawler.log
```

## 🔧 개발 및 확장

### 새로운 기능 추가
1. `src/` 디렉토리에 새로운 모듈 추가
2. `main.py`에서 해당 모듈 import
3. 설정 파일에 필요한 설정 추가

### 테스트
```bash
# 테스트 실행
python -m pytest tests/
```

### 코드 품질
```bash
# 코드 포맷팅
black src/
# 린팅
flake8 src/
```

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 상업적 사용 시 해당 웹사이트의 이용약관을 준수해주세요.

## 🤝 기여

버그 리포트, 기능 제안, 코드 기여를 환영합니다!

1. 이슈 생성
2. 포크 생성
3. 브랜치 생성
4. 변경사항 커밋
5. Pull Request 생성

## 📞 지원

문제가 발생하거나 질문이 있으시면:
- 이슈 페이지에 등록
- 로그 파일 확인 후 상세 정보 제공

---

**버전**: 1.0.0  
**최종 업데이트**: 2024년 7월 31일  
**작성자**: AI Assistant 