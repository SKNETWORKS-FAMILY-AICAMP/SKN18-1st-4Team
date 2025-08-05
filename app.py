import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from database.database import connect_db
from utilities.app_utility import get_vehicle_registration_data, get_environmental_impact_data

# 페이지 설정
st.set_page_config(
    page_title="친환경 자동차 대시보드",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 친환경 자동차 대시보드")

# 탭 생성
tab1, tab2 = st.tabs(["자동차 등록 현황 분석", "환경 영향 분석"])

with tab1:
    st.header("자동차 등록 현황 분석")
    
    # 데이터 가져오기
    vehicle_data = get_vehicle_registration_data()
    
    if vehicle_data is not None and not vehicle_data.empty:
        # 차종별 하이라이트 기능
        highlight_option = st.selectbox(
            "하이라이트할 차종을 선택하세요:",
            ["전체", "전기차", "수소차", "하이브리드"]
        )
        
        # 전체 선택 시에만 이중 축 그래프 표시
        if highlight_option == "전체":
            # 이중 축 그래프 생성
            fig = make_subplots(
                specs=[[{"secondary_y": True}]]
            )
            
            # 첫 번째 그래프: 전체 자동차 등록대수 (선그래프)
            fig.add_trace(
                go.Scatter(
                    x=vehicle_data['year'],
                    y=vehicle_data['total_vehicles'],
                    name="전체 자동차 등록대수",
                    line=dict(color="#ffafcc", width=3),
                    mode='lines+markers'
                ),
                secondary_y=False
            )
            
            # 두 번째 그래프: 친환경 자동차 등록대수 (스택형 막대그래프)
            # 전체 선택 시 모든 항목을 원래 색상으로 표시
            fig.add_trace(
                go.Bar(
                    x=vehicle_data['year'],
                    y=vehicle_data['electric_vehicles'],
                    name="전기차",
                    marker_color='#0096c7',
                    marker_opacity=1.0,
                    hovertemplate='전기차: %{y:,.0f}대<br>비율: %{customdata:.1f}%<extra></extra>',
                    customdata=vehicle_data['electric_ratio']
                ),
                secondary_y=True
            )
            
            fig.add_trace(
                go.Bar(
                    x=vehicle_data['year'],
                    y=vehicle_data['hydrogen_vehicles'],
                    name="수소차",
                    marker_color='#00b4d8',
                    marker_opacity=1.0,
                    hovertemplate='수소차: %{y:,.0f}대<br>비율: %{customdata:.1f}%<extra></extra>',
                    customdata=vehicle_data['hydrogen_ratio']
                ),
                secondary_y=True
            )
            
            fig.add_trace(
                go.Bar(
                    x=vehicle_data['year'],
                    y=vehicle_data['hybrid_vehicles'],
                    name="하이브리드",
                    marker_color='#ade8f4',
                    marker_opacity=1.0,
                    hovertemplate='하이브리드: %{y:,.0f}대<br>비율: %{customdata:.1f}%<extra></extra>',
                    customdata=vehicle_data['hybrid_ratio']
                ),
                secondary_y=True
            )
            
            # 그래프 업데이트
            fig.update_layout(
                title="연도별 자동차 등록 현황 - 전체",
                xaxis_title="연도",
                barmode='stack',
                height=600
            )
            
            # Y축 눈금 개수를 동일하게 설정 (5개 간격)
            fig.update_yaxes(
                title_text="전체 자동차 등록대수", 
                secondary_y=False, 
                range=[20000000, 27000000],
                dtick=1750000  # (27000000-20000000)/4 = 1750000
            )
            fig.update_yaxes(
                title_text="친환경 자동차 등록대수", 
                secondary_y=True, 
                range=[0, 4000000],
                dtick=1000000  # (4000000-0)/4 = 1000000
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        
        # 선택된 차종의 상세 정보 표시
        if highlight_option != "전체":
            st.subheader(f"📊 {highlight_option} 상세 정보")
            
            if highlight_option == "전기차":
                selected_data = vehicle_data['electric_vehicles']
                selected_ratio = vehicle_data['electric_ratio']
            elif highlight_option == "수소차":
                selected_data = vehicle_data['hydrogen_vehicles']
                selected_ratio = vehicle_data['hydrogen_ratio']
            elif highlight_option == "하이브리드":
                selected_data = vehicle_data['hybrid_vehicles']
                selected_ratio = vehicle_data['hybrid_ratio']


            color_map = {
                "전기차": "#0096c7",
                "수소차": "#00b4d8",
                "하이브리드": "#ade8f4"
            }
            
            # 선택된 차종의 연도별 변화 그래프
            fig_detail = go.Figure()
            fig_detail.add_trace(go.Bar(
                x=vehicle_data['year'],
                y=selected_ratio,  # 등록대수 대신 비율 사용
                name=highlight_option,
                marker_color=color_map.get(highlight_option),
                hovertemplate=f'{highlight_option} 비율: %{{y:.1f}}%<extra></extra>'
            ))
            
            # 차종별 Y축 범위 설정
            if highlight_option == "전기차":
                y_max = 40
            elif highlight_option == "수소차":
                y_max = 5
            elif highlight_option == "하이브리드":
                y_max = 100
            
            fig_detail.update_layout(
                title=f"{highlight_option} 연도별 비율 변화",
                xaxis_title="연도",
                yaxis_title=f"{highlight_option} 비율 (%)",
                height=400,
                yaxis=dict(range=[0, y_max])  # 차종별로 다른 Y축 범위 설정
            )
            
            st.plotly_chart(fig_detail, use_container_width=True)
            
            # 선택된 차종의 통계 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"2024년 {highlight_option} 등록대수", f"{selected_data.iloc[-1]:,.0f}대")
            with col2:
                growth_rate = ((selected_data.iloc[-1] - selected_data.iloc[0]) / selected_data.iloc[0]) * 100
                st.metric("2020년 대비 증가율", f"{growth_rate:.1f}%")
            with col3:
                st.metric(f"{highlight_option} 비율", f"{selected_ratio.iloc[-1]:.1f}%")
    else:
        st.warning("데이터베이스에서 자동차 등록 현황 데이터를 가져올 수 없습니다.")

with tab2:
    st.header("환경 영향 분석")
    
    # 데이터 가져오기
    env_data = get_environmental_impact_data()
    
    if env_data is not None and not env_data.empty:
        # 이중 축 그래프 생성
        fig = make_subplots(
            specs=[[{"secondary_y": True}]]
        )
        
        # 첫 번째 그래프: 온실가스 배출량 (선그래프)
        fig.add_trace(
            go.Scatter(
                x=env_data['year'],
                y=env_data['greenhouse_gas'],
                name="온실가스 배출량",
                line=dict(color='#8a9a5b', width=3),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        
        # 두 번째 그래프: 친환경 자동차 비율 (막대그래프)
        fig.add_trace(
            go.Bar(
                x=env_data['year'],
                y=env_data['eco_vehicle_ratio'],
                name="친환경 자동차 비율",
                marker_color= '#a4de02',
                hovertemplate='친환경차 비율: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig.update_layout(
            title="연도별 환경 영향 분석",
            xaxis_title="연도",
            height=500
        )
        
        # x축을 1년 단위로 설정
        fig.update_xaxes(
            dtick=1,  # 1년 단위로 눈금 표시
            tickmode='linear'
        )
        
        fig.update_yaxes(
            title_text="친환경 자동차 비율 (%)", 
            secondary_y=False, 
            range=[0, 20],
            dtick=5  # (20-0)/4 = 5
        )
        fig.update_yaxes(
            title_text="온실가스 배출량", 
            secondary_y=True,
            range=[70000, 90000],
            dtick=5000  # (90000-70000)/4 = 5000
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 추가 분석: 지역별 온실가스 배출량 분석
        st.subheader("🌍 지역별 온실가스 배출량 분석")
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            # 실제 사용 가능한 최신 연도(2022년)로 수정
            region_gas_query = """
            SELECT 
                년도 as year,
                지역 as region,
                승용 as passenger,
                승합 as bus,
                화물 as cargo,
                특수 as special
            FROM greenhouse_gases 
            WHERE 년도 = 2022
            ORDER BY 지역
            """
            cursor.execute(region_gas_query)
            data = cursor.fetchall()
            columns = ['year', 'region', 'passenger', 'bus', 'cargo', 'special']
            region_gas_data = pd.DataFrame(data, columns=columns)
            cursor.close()
            conn.close()
            
            if not region_gas_data.empty:
                # 지역별 총 온실가스 배출량 계산
                region_gas_data['total_gas'] = region_gas_data['passenger'] + region_gas_data['bus'] + region_gas_data['cargo'] + region_gas_data['special']
                
                # 지역별 온실가스 배출량 차트
                fig_region = go.Figure()
                fig_region.add_trace(go.Bar(
                    x=region_gas_data['region'],
                    y=region_gas_data['total_gas'],
                    name='총 온실가스 배출량',
                    marker_color='#8a9a5b',
                    hovertemplate='지역: %{x}<br>배출량: %{y:,}<extra></extra>'
                ))
                
                fig_region.update_layout(
                    title="2022년 지역별 온실가스 배출량",
                    xaxis_title="지역",
                    yaxis_title="온실가스 배출량",
                    height=400
                )
                
                st.plotly_chart(fig_region, use_container_width=True)
                
                # 지역별 상세 분석
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📊 지역별 배출량 순위")
                    
                    # 단위 표시를 위한 컨테이너
                    unit_container = st.container()
                    with unit_container:
                        # CSS를 사용해서 단위를 오른쪽 상단에 배치
                        st.markdown(
                            """
                            <style>
                            .unit-text {
                                text-align: right;
                                font-size: 14px;
                                color: #666;
                                margin-bottom: 5px;
                            }
                            </style>
                            <div class="unit-text">단위: 톤CO₂</div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    region_ranking = region_gas_data.sort_values('total_gas', ascending=False)
                    # 순위 추가 (1부터 시작)
                    region_ranking['rank'] = range(1, len(region_ranking) + 1)
                    region_ranking = region_ranking[['rank', 'region', 'total_gas']].rename(columns={
                        'rank': '순위',
                        'region': '지역',
                        'total_gas': '총 배출량'
                    })
                    # 총 배출량에 1,000 단위 구분 쉼표 추가
                    region_ranking['총 배출량'] = region_ranking['총 배출량'].apply(lambda x: f"{x:,}")
                    st.dataframe(region_ranking, use_container_width=True, hide_index=True)

                with col2:
                    st.subheader("📈 차종별 배출량 분석")
                    
                    # 단위 표시를 위한 컨테이너
                    unit_container2 = st.container()
                    with unit_container2:
                        # CSS를 사용해서 단위를 오른쪽 상단에 배치
                        st.markdown(
                            """
                            <style>
                            .unit-text2 {
                                text-align: right;
                                font-size: 14px;
                                color: #666;
                                margin-bottom: 5px;
                            }
                            </style>
                            <div class="unit-text2">단위: 톤CO₂</div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    vehicle_types = ['passenger', 'bus', 'cargo', 'special']
                    vehicle_names = ['승용', '승합', '화물', '특수']
                    
                    for i, (vehicle_type, vehicle_name) in enumerate(zip(vehicle_types, vehicle_names)):
                        total_emission = region_gas_data[vehicle_type].sum()
                        st.metric(f"{vehicle_name} 총 배출량", f"{total_emission:,}")
            else:
                st.warning("지역별 온실가스 배출량 데이터를 가져올 수 없습니다.")
        except Exception as e:
            st.warning("지역별 온실가스 배출량 데이터를 가져올 수 없습니다.")
    else:
        st.warning("데이터베이스에서 환경 영향 분석 데이터를 가져올 수 없습니다.") 
