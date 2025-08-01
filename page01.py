import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def create_bar_chart():
    # 제목
    st.title("국내 자동차 점유율 대비")

    # CSV 파일 불러오기
    df = pd.read_csv("차종별_차량수.csv", header=[0])

    # 드롭다운
    if "시도명" in df.columns:
        # '전체' 옵션을 드롭다운 맨 앞에 추가
        options = ['전체'] + list(df['시도명'].unique())
        selected_region = st.selectbox("시도명을 선택하세요", options)
        
        if selected_region == '전체':
            filtered_df = df
            # 전체 데이터에서 '계'가 아닌 데이터만 사용
            df_for_chart = df[df['시군명'] != '계']
        else:
            filtered_df = df[df['시도명'] == selected_region]
            # 선택된 시도에서 '계'가 아닌 데이터만 사용
            df_for_chart = filtered_df[filtered_df['시군명'] != '계']

    # 테이블로 보여주기
    st.subheader(f"📝 {selected_region} 지역 데이터")
    st.dataframe(filtered_df)
    
    # 막대 그래프 생성
    st.subheader("📊 자동차 등록 현황")
    
    # 차종별 데이터 준비
    plot_data = pd.melt(
        df_for_chart,
        id_vars=['시도명', '시군명'],
        value_vars=['승용차', '승합차', '화물차', '특수차'],
        var_name='차종',
        value_name='등록대수'
    )
    
    # 막대 그래프 생성
    title = f"{'전국' if selected_region == '전체' else selected_region} 차종별 등록 현황"
    
    fig = px.bar(
        plot_data,
        x='시군명' if selected_region != '전체' else '시도명',
        y='등록대수',
        color='차종',
        title=title,
        barmode='group',  # 그룹화된 막대 그래프
        text='등록대수'  # 막대 위에 값 표시
    )

    # 그래프 레이아웃 수정
    fig.update_layout(
        xaxis_title='지역',
        yaxis_title='등록대수',
        width=1000,
        height=600,
        plot_bgcolor='white',  # 배경색 흰색으로 설정
        legend_title='차종',
        showlegend=True
    )
    
    # x축 레이블 45도 회전
    fig.update_xaxes(tickangle=45)
    
    # 막대 위의 텍스트 위치 조정
    fig.update_traces(
        textposition='outside',  # 막대 위에 텍스트 표시
        texttemplate='%{text:,.0f}'  # 천 단위 구분기호 사용, 소수점 제거
    )

    # 그래프 표시a
    st.plotly_chart(fig)

if __name__ == "__main__":
    create_bar_chart()
