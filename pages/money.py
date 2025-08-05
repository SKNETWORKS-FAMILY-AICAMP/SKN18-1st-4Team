import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from database.database import connect_db
from utilities.money_utility import get_announcement_data, get_subsidy_data, get_top5_models
import numpy as np
import json

# 페이지 설정
st.set_page_config(
    page_title="보조금 정보",
    page_icon="💰",
    layout="wide"
)

st.title("💰 친환경 자동차 보조금 정보")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["공고 현황 분석", "보조금 정보", "지역별 정책 활용 현황"])

# ------------------------- 공고 현황 분석 ---------------------------------------------------
with tab1:
    st.header("공고 현황 분석")

    # 데이터 가져오기
    car_type = st.selectbox("차종 선택:", ["전기차", "수소차"])
    vehicle_type = "electric" if car_type == "전기차" else "hydrogen"
    announcement_data = get_announcement_data(vehicle_type)

    if announcement_data is not None and not announcement_data.empty:
        # 스택형 막대그래프 생성
        fig = go.Figure()

        # 출고대수 (실제 출고된 수량)
        fig.add_trace(go.Bar(
            x=announcement_data['year'],
            y=announcement_data['released_count'],
            name='출고대수',
            marker_color='#add8e6',
            hovertemplate='출고대수: %{y:,}대<br>비율: %{customdata:.1f}%<extra></extra>',
            customdata=announcement_data['released_ratio']
        ))

        # 출고잔여대수 (출고되지 않은 잔여 수량)
        fig.add_trace(go.Bar(
            x=announcement_data['year'],
            y=announcement_data['remaining_count'],
            name='출고잔여대수',
            marker_color='#f9c5d1',
            hovertemplate='잔여대수: %{y:,}대<br>비율: %{customdata:.1f}%<extra></extra>',
            customdata=announcement_data['remaining_ratio']
        ))

        fig.update_layout(
            title="연도별 민간공고 현황",
            xaxis_title="연도",
            yaxis_title="대수",
            barmode='stack',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)



# ------------------------- 보조금 정보 ---------------------------------------------------
with tab2:
    st.header("보조금 정보")

    # 차종 선택
    car_type = st.selectbox("차종 선택:", ["전기차", "수소차"], key = "elect_hydrogen")

    # 테이블명 결정
    table_name = "money_electronic_car" if car_type == "전기차" else "money_hydrogen_car"
    vehicle_name = "전기차" if car_type == "전기차" else "수소차"

    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # 전체 데이터 조회
            st.subheader(f"{vehicle_name} 전체 데이터")
            all_data = pd.read_sql(f"SELECT * FROM {table_name} WHERE 시도 NOT LIKE '%합계%' AND 모델명 NOT LIKE '%합계%'", conn)
            
            # 보조금 컬럼에서 쉼표 제거 후 int로 변환
            all_data['보조금(만원)'] = all_data['보조금(만원)'].str.replace(',', '').astype(str)
            all_data['보조금(만원)'] = pd.to_numeric(all_data['보조금(만원)'], errors='coerce').fillna(0).astype(int)
            
            # 국비(만원), 지방비(만원) 컬럼 삭제
            all_data = all_data.drop(columns=['국비(만원)', '지방비(만원)'])
            
            # 보조금 내림차순으로 정렬
            all_data = all_data.sort_values('보조금(만원)', ascending=False)
            
            # 인덱스를 1부터 시작하는 순번으로 변경
            all_data = all_data.reset_index(drop=True)
            all_data.index = all_data.index + 1
            all_data.index.name = '순위'
            
            # 보조금 컬럼에 쉼표 추가하여 표시
            all_data['보조금(만원)'] = all_data['보조금(만원)'].apply(lambda x: f"{x:,}")
            
            st.dataframe(all_data, use_container_width=True)
            
            # 지역별 보조금 Top 5
            if '보조금(만원)' in all_data.columns and '시도' in all_data.columns:
                st.subheader("지역별 보조금 Top 5")
                
                # 모든 지역을 드롭다운으로 선택
                all_regions = sorted(all_data['시도'].unique())
                selected_region = st.selectbox(
                    "지역 선택:",
                    options=all_regions
                )
                
                # 선택된 지역의 데이터 필터링
                selected_region_data = all_data[all_data['시도'] == selected_region]
                
                if not selected_region_data.empty:
                    # 중복값 제거 (순위 컬럼 제외한 모든 컬럼 기준)
                    selected_region_data = selected_region_data.drop_duplicates()
                    
                    # 보조금 내림차순으로 정렬하여 상위 5개 선택
                    top5_data = selected_region_data.sort_values('보조금(만원)', ascending=False).head(5)
                    
                    # 인덱스를 1부터 시작하는 순번으로 변경
                    top5_data = top5_data.reset_index(drop=True)
                    top5_data.index = top5_data.index + 1
                    top5_data.index.name = '순위'
                    
                    st.dataframe(top5_data, use_container_width=True)
                    
                else:
                    st.warning(f"{selected_region} 지역에 데이터가 없습니다.")
        
        else:
            st.error(f"{table_name} 테이블이 존재하지 않습니다.")
            st.info("데이터베이스에 해당 테이블이 있는지 확인해주세요.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        st.error(f"데이터베이스 연결 또는 데이터 조회 실패: {e}")
        st.info("데이터베이스 연결 상태와 테이블 존재 여부를 확인해주세요.")


# -------------------------지역별 정책 활용 현황---------------------------------------------------
with tab3:
    st.header("지역별 정책 활용 현황")

    car_type = st.selectbox("차종 선택:", ["전기차", "수소차"], key = "vehicle_type_select")
    table_name = "electronic_car" if car_type == "전기차" else "hydrogen_car"

    # --- 연도별 데이터 로드 ---
    try:
        conn = connect_db()
        years_df = pd.read_sql(f"SELECT DISTINCT 년도 AS year FROM {table_name} ORDER BY 년도", conn)
        years = years_df["year"].tolist()
        sel_year = st.selectbox("연도 선택:", years, index=(len(years) - 1 if years else 0), key = "year_select")

        sql = f"""
        SELECT 
            지역 AS region,
            민간공고대수 AS announced_count,
            출고잔여대수 AS remaining_count
        FROM {table_name}
        WHERE 년도 = %s
        """
        df = pd.read_sql(sql, conn, params=[sel_year])
        conn.close()
    except Exception as e:
        df = pd.DataFrame()
        st.warning("에러 발생: " + str(e))

    if not df.empty:
        # --- 지역별 데이터 합산 ---
        region_summary = (df.groupby("region", as_index=False)
                            .agg(announced_count=("announced_count", "sum"),
                                remaining_count=("remaining_count", "sum")))
        region_summary["released_count"] = (region_summary["announced_count"] - region_summary["remaining_count"]).clip(lower=0)

        safe_den = region_summary["announced_count"].replace(0, np.nan)
        region_summary["정책활용도(%)"] = (region_summary["released_count"] / safe_den * 100).round(1).fillna(0)

        # --- GeoJSON 로드 ---
        geojson_path = "./skorea-provinces-geo.json"
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                korea_geo = json.load(f)
        except FileNotFoundError:
            korea_geo = None
            st.warning("GeoJSON 파일을 찾을 수 없어. 경로를 확인해줘: ./skorea-provinces-geo.json")

        # --- 지역명 키 자동 감지 ---
        def detect_featureid_key(geo):
            if not geo or "features" not in geo or not geo["features"]:
                return None
            props = geo["features"][0].get("properties", {})
            for k in ["CTP_KOR_NM", "CTP_ENG_NM", "NAME_1", "name"]:
                if k in props:
                    return f"properties.{k}"
            return f"properties.{list(props.keys())[0]}" if props else None

        featureidkey = detect_featureid_key(korea_geo) if korea_geo else None

        # --- 지역명 매핑 테이블 ---
        kor_to_eng = {
            "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon",
            "광주": "Gwangju", "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong",
            "경기": "Gyeonggi-do", "강원": "Gangwon-do",
            "충북": "Chungcheongbuk-do", "충남": "Chungcheongnam-do",
            "전북": "Jeollabuk-do", "전남": "Jeollanam-do",
            "경북": "Gyeongsangbuk-do", "경남": "Gyeongsangnam-do",
            "제주": "Jeju",
        }

        def normalize_for_geo(name, featureidkey_str):
            key = featureidkey_str.split(".")[-1] if featureidkey_str else ""
            if key in ["CTP_KOR_NM", "name"]:
                return name
            return kor_to_eng.get(name, name)

        if korea_geo and featureidkey:
            region_summary["지도매칭명"] = region_summary["region"].apply(
                lambda x: normalize_for_geo(x, featureidkey)
            )

            # --- Choropleth 지도 출력 ---
            st.markdown(f"{sel_year}년 {car_type} 정책활용도(%)")
            fig_map = px.choropleth(
                region_summary,
                geojson=korea_geo,
                locations="지도매칭명",
                featureidkey=featureidkey,
                color="정책활용도(%)", 
                hover_data={
                    "region": True,
                    "announced_count": ":,",
                    "remaining_count": ":,",
                    "정책활용도(%)": ":.1f",
                    "지도매칭명": False
                },
                labels={
                    "region": "지역",
                    "announced_count": "민간공고대수",
                    "remaining_count": "출고잔여대수",
                    "정책활용도(%)": "정책활용도(%)"
                }
            )
            fig_map.update_coloraxes(cmin=0, cmax=100)
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                height=1000,
                margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_colorbar=dict(title="정책활용도(%)")
            )
            st.plotly_chart(fig_map, use_container_width=True)

        else:
            st.info("GeoJSON을 불러오지 못함.")
    else:
        st.warning("선택한 연도에 대한 데이터를 찾지 못함")

