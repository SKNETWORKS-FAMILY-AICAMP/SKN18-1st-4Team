import pandas as pd
import numpy as np
from database.database import connect_db

def get_announcement_data(vehicle_type="electric"):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        table_name = "electronic_car" if vehicle_type == "electric" else "hydrogen_car"
        
        # electronic_car 테이블에서 공고 현황 데이터 가져오기
        query = f"""
        SELECT 
            년도 as year,
            지역 as region,
            차종 as vehicle_type,
            민간공고대수 as announced_count,
            출고대수 as released_count,
            출고잔여대수 as remaining_count
        FROM {table_name}
        WHERE 년도 BETWEEN 2020 AND 2024
        ORDER BY 년도, 지역
        """
        
        cursor.execute(query)
        data = cursor.fetchall()
        columns = ['year', 'region', 'vehicle_type', 'announced_count', 'released_count', 'remaining_count']
        df = pd.DataFrame(data, columns=columns)
        
        cursor.close()
        conn.close()
        
        if df.empty:
            return None
        
        # 연도별로 데이터 집계
        yearly_data = df.groupby('year').agg({
            'announced_count': 'sum',
            'released_count': 'sum',
            'remaining_count': 'sum'
        }).reset_index()
        
        # 비율 계산
        yearly_data['released_ratio'] = (yearly_data['released_count'] / yearly_data['announced_count']) * 100
        yearly_data['remaining_ratio'] = (yearly_data['remaining_count'] / yearly_data['announced_count']) * 100
        
        return yearly_data
        
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def get_subsidy_data(vehicle_type):
    """
    보조금 정보를 가져오는 함수
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        if vehicle_type == "electric":
            # 전기차 보조금 정보 (money_electronic_car 테이블 사용)
            query = """
            SELECT 
                시도 as region,
                모델명 as vehicle_type,
                CAST(REPLACE(보조금(만원), ',', '') AS SIGNED) as total_subsidy
            FROM money_electronic_car 
            WHERE 시도 NOT LIKE '%합계%' AND 모델명 NOT LIKE '%합계%'
            ORDER BY total_subsidy DESC
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            columns = ['region', 'vehicle_type', 'total_subsidy']
            df = pd.DataFrame(data, columns=columns)
            
            if df.empty:
                return None
            
            # 컬럼명 변경
            df = df.rename(columns={
                'region': '시도',
                'vehicle_type': '모델명',
                'total_subsidy': '보조금(만원)'
            })
            
        elif vehicle_type == "hydrogen":
            # 수소차 보조금 정보 (money_hydrogen_car 테이블 사용)
            query = """
            SELECT 
                시도 as region,
                모델명 as vehicle_type,
                CAST(REPLACE(보조금(만원), ',', '') AS SIGNED) as total_subsidy
            FROM money_hydrogen_car 
            WHERE 시도 NOT LIKE '%합계%' AND 모델명 NOT LIKE '%합계%'
            ORDER BY total_subsidy DESC
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            columns = ['region', 'vehicle_type', 'total_subsidy']
            df = pd.DataFrame(data, columns=columns)
            
            if df.empty:
                return None
            
            # 컬럼명 변경
            df = df.rename(columns={
                'region': '시도',
                'vehicle_type': '모델명',
                'total_subsidy': '보조금(만원)'
            })
        
        cursor.close()
        conn.close()
        return df
        
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def get_top5_models(region, vehicle_type="electric"):
    """
    지역별 TOP5 모델 정보를 가져오는 함수
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 테이블 선택
        table_name = "money_electronic_car" if vehicle_type == "electric" else "money_hydrogen_car"
        
        if region == "전체":
            # 전체 지역 TOP5 - 보조금 기준으로 정렬
            query = f"""
            SELECT 
                시도 as region,
                모델명 as vehicle_type,
                CAST(REPLACE(보조금(만원), ',', '') AS SIGNED) as total_subsidy
            FROM {table_name}
            WHERE 시도 NOT LIKE '%합계%' AND 모델명 NOT LIKE '%합계%'
            ORDER BY total_subsidy DESC
            LIMIT 5
            """
        else:
            # 특정 지역 TOP5 - 보조금 기준으로 정렬
            query = f"""
            SELECT 
                시도 as region,
                모델명 as vehicle_type,
                CAST(REPLACE(보조금(만원), ',', '') AS SIGNED) as total_subsidy
            FROM {table_name}
            WHERE 시도 = '{region}' AND 시도 NOT LIKE '%합계%' AND 모델명 NOT LIKE '%합계%'
            ORDER BY total_subsidy DESC
            LIMIT 5
            """
        
        cursor.execute(query)
        data = cursor.fetchall()
        columns = ['region', 'vehicle_type', 'total_subsidy']
        df = pd.DataFrame(data, columns=columns)
        
        cursor.close()
        conn.close()
        
        if df.empty:
            return None
        
        # 순위 추가 (보조금 기준으로 이미 정렬되어 있음)
        df['rank'] = range(1, len(df) + 1)
        
        # 컬럼명 변경
        df = df.rename(columns={
            'rank': '순위',
            'region': '시도',
            'vehicle_type': '모델명',
            'total_subsidy': '보조금(만원)'
        })
        
        return df
        
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None 