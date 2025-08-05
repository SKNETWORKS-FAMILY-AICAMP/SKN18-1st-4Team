import streamlit as st
from utilities.faq_utility import get_faq_data, get_categories, filter_faq_by_category, search_faq
import math

st.markdown(
    """
    <h1 style='text-align: center;'>자주하는 질문</h1>
    <p style='text-align: center;'>자주하는 질문을 확인해 보세요</p>
    """,
    unsafe_allow_html=True
)

# 검색 기능
search_term = st.text_input("검색", "궁금한 점을 검색해 보세요.")

# 세션 상태 초기화
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = ""
if 'selected_subcategory' not in st.session_state:
    st.session_state.selected_subcategory = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# CSS 스타일 적용
st.markdown("""
<style>
    .button-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    .grid-button {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        padding: 20px 15px;
        text-align: center;
        cursor: pointer;
        transition: background-color 0.2s;
        font-size: 16px;
        font-weight: 500;
    }
    
    .grid-button:hover {
        background-color: #e9ecef;
    }
    
    .grid-button.active {
        background-color: #17a2b8;
        color: white;
    }
    
    .grid-button:first-child {
        background-color: #17a2b8;
        color: white;
    }
    
    .stButton > button {
        width: 100%;
        height: 100%;
        border: none;
        background: transparent;
        color: inherit;
        font-size: inherit;
        font-weight: inherit;
        padding: 20px 15px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #e9ecef;
    }
    
    .stButton > button.active {
        background-color: #17a2b8;
        color: white;
    }
    
    .subcategory-button {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        padding: 10px 15px;
        margin: 5px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s;
        font-size: 12px;
    }
    
    .subcategory-button:hover {
        background-color: #e9ecef;
    }
    
    .subcategory-button.active {
        background-color: #17a2b8;
        color: white;
    }
    
    .faq-accordion {
        margin: 20px 0;
    }
    
    .faq-item {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 10px;
        overflow: hidden;
    }
    
    .faq-question {
        background-color: #f8f9fa;
        padding: 15px;
        cursor: pointer;
        font-weight: 500;
        border-bottom: 1px solid #ddd;
    }
    
    .faq-answer {
        padding: 15px;
        background-color: white;
    }
    
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
        gap: 10px;
    }
    
    .page-info {
        margin: 0 15px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# FAQ 데이터 가져오기
try:
    df = get_faq_data()
    categories = get_categories()
    
    # Streamlit 버튼 그리드 생성
    with st.container():
        # 2행 4열 그리드 레이아웃
        for row in range(2):
            cols = st.columns(4)
            for col in range(4):
                index = row * 4 + col
                if index < len(categories) and categories[index]:
                    # 선택된 카테고리에 따라 버튼 스타일 변경
                    button_type = "primary" if st.session_state.selected_category == categories[index] else "secondary"
                    
                    if cols[col].button(categories[index], key=f"btn_{index}", type=button_type):
                        st.session_state.selected_category = categories[index]
                        st.session_state.selected_subcategory = ""  # 하위 카테고리 선택 초기화
                        st.session_state.current_page = 1  # 페이지 초기화
                        st.rerun()

    st.write("---")

    # FAQ 데이터 필터링 및 표시
    if st.session_state.selected_category:
        # 카테고리별 필터링
        filtered_df = filter_faq_by_category(df, st.session_state.selected_category)
        
        # 검색어 필터링
        if search_term and search_term != "궁금한 점을 검색해 보세요.":
            filtered_df = search_faq(filtered_df, search_term)
        
        # 결과 표시
        if not filtered_df.empty:
            st.markdown(f"### {st.session_state.selected_category} 카테고리 FAQ")
            
            # top 10 카테고리인지 확인
            is_top_10 = st.session_state.selected_category.lower() == "top 10"
            
            if is_top_10:
                # top 10 카테고리는 페이지네이션 없이 모든 항목 표시
                st.markdown(f"**총 {len(filtered_df)}개의 FAQ**")
                
                # 아코디언 형식으로 FAQ 표시
                for index, row in filtered_df.iterrows():
                    # question 컬럼에서 질문 가져오기
                    question = row.get('question', '')
                    if not question:
                        # question 컬럼이 없으면 다른 컬럼에서 찾기
                        for col in filtered_df.columns:
                            if 'question' in col.lower():
                                question = row.get(col, '')
                                break
                    
                    # answer 컬럼에서 답변 가져오기
                    answer = row.get('answer', '')
                    if not answer:
                        # answer 컬럼이 없으면 다른 컬럼에서 찾기
                        for col in filtered_df.columns:
                            if 'answer' in col.lower():
                                answer = row.get(col, '')
                                break
                    
                    # 질문이나 답변이 없으면 기본값 설정
                    if not question:
                        question = f"FAQ {index + 1}"
                    if not answer:
                        answer = "답변 내용이 없습니다."
                    
                    # 아코디언 생성 - 질문만 표시하고 클릭하면 답변 표시
                    with st.expander(f" {question}", expanded=False):
                        st.markdown(f"** 답변:** {answer}")
            else:
                # 다른 카테고리는 페이지네이션 적용
                # 페이지네이션 설정
                items_per_page = 5
                total_items = len(filtered_df)
                total_pages = math.ceil(total_items / items_per_page)
                
                # 현재 페이지가 유효한 범위인지 확인
                if st.session_state.current_page > total_pages:
                    st.session_state.current_page = 1
                
                # 현재 페이지의 데이터 계산
                start_idx = (st.session_state.current_page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, total_items)
                
                # 페이지 정보 표시
                st.markdown(f"**총 {total_items}개의 FAQ 중 {start_idx + 1}-{end_idx}번째 항목**")
                
                # 현재 페이지의 FAQ 항목들 표시
                current_page_df = filtered_df.iloc[start_idx:end_idx]
                
                # 아코디언 형식으로 FAQ 표시
                for index, row in current_page_df.iterrows():
                    # question 컬럼에서 질문 가져오기
                    question = row.get('question', '')
                    if not question:
                        # question 컬럼이 없으면 다른 컬럼에서 찾기
                        for col in current_page_df.columns:
                            if 'question' in col.lower():
                                question = row.get(col, '')
                                break
                    
                    # answer 컬럼에서 답변 가져오기
                    answer = row.get('answer', '')
                    if not answer:
                        # answer 컬럼이 없으면 다른 컬럼에서 찾기
                        for col in current_page_df.columns:
                            if 'answer' in col.lower():
                                answer = row.get(col, '')
                                break
                    
                    # 질문이나 답변이 없으면 기본값 설정
                    if not question:
                        question = f"FAQ {index + 1}"
                    if not answer:
                        answer = "답변 내용이 없습니다."
                    
                    # 아코디언 생성 - 질문만 표시하고 클릭하면 답변 표시
                    with st.expander(f" {question}", expanded=False):
                        st.markdown(f"** 답변:** {answer}")
                
                # 페이지네이션 컨트롤
                if total_pages > 1:
                    st.write("---")
                    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                    
                    with col1:
                        if st.button("◀ 이전", disabled=st.session_state.current_page == 1, use_container_width=True):
                            st.session_state.current_page -= 1
                            st.rerun()
                    
                    with col2:
                        if st.button("처음", disabled=st.session_state.current_page == 1, use_container_width=True):
                            st.session_state.current_page = 1
                            st.rerun()
                    
                    with col3:
                        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; height: 100%; padding: 10px; font-weight: 500;'>페이지 {st.session_state.current_page} / {total_pages}</div>", 
                                   unsafe_allow_html=True)
                    
                    with col4:
                        if st.button("마지막", disabled=st.session_state.current_page == total_pages, use_container_width=True):
                            st.session_state.current_page = total_pages
                            st.rerun()
                    
                    with col5:
                        if st.button("다음 ▶", disabled=st.session_state.current_page == total_pages, use_container_width=True):
                            st.session_state.current_page += 1
                            st.rerun()
        else:
            st.warning(f"'{st.session_state.selected_category}' 카테고리에 해당하는 FAQ가 없습니다.")
    else:
        st.info("위의 카테고리 버튼을 클릭하여 FAQ를 확인하세요.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
    st.info("데이터베이스 연결을 확인해주세요.")