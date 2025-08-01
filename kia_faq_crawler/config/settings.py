# 기아자동차 FAQ 크롤링 설정 파일

# 웹사이트 설정
WEBSITE_URL = "https://www.kia.com/kr/customer-service/center/faq"
LANGUAGE = "ko"

# 셀렉터 설정
SELECTORS = {
    "category": "span.name",
    "item": ".cmp-accordion__item",
    "question": ":scope span.cmp-accordion__title",
    "answer": ":scope div.cmp-accordion__panel p",
    "answer_links": ":scope div.cmp-accordion__panel a",
    "pagination": {
        "container": ".cmp-pagination__wrap",
        "page_numbers": ".paging-list li a",
        "next_button": ".cmp-pagination__next",
        "current_page": ".paging-list li.is-active a"
    }
}

# 브라우저 설정
BROWSER_CONFIG = {
    "headless": True,
    "slow_mo": 100,
    "timeout": 30000
}

# 크롤링 설정
CRAWLING_CONFIG = {
    "delay_between_requests": 1.0,
    "max_retries": 3,
    "retry_delay": 2.0
}

# 파일 설정
FILE_CONFIG = {
    "output_dir": "data/processed",
    "raw_dir": "data/raw",
    "reports_dir": "data/reports",
    "logs_dir": "logs"
}

# 로깅 설정
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/kia_faq_crawler.log"
} 