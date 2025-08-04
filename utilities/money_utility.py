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
            # 전기차 보조금 정보 (electronic_car 테이블 사용)
            query = """
            SELECT 
                지역 as region,
                차종 as vehicle_type,
                민간공고대수 as national_subsidy,
                출고대수 as local_subsidy
            FROM electronic_car 
            WHERE 년도 = 2024
            ORDER BY 지역
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            columns = ['region', 'vehicle_type', 'national_subsidy', 'local_subsidy']
            df = pd.DataFrame(data, columns=columns)
            
            if df.empty:
                return None
            
            # 컬럼명 변경
            df = df.rename(columns={
                'region': '지역',
                'vehicle_type': '차종',
                'national_subsidy': '민간공고대수',
                'local_subsidy': '출고대수'
            })
            
        elif vehicle_type == "hydrogen":
            # 수소차 보조금 정보 (hydrogen_car 테이블 사용)
            query = """
            SELECT 
                지역 as region,
                차종 as vehicle_type,
                CAST(민간공고대수 AS SIGNED) as subsidy_amount
            FROM hydrogen_car 
            WHERE 년도 = 2024
            ORDER BY 지역
            """
            
            cursor.execute(query)
            data = cursor.fetchall()
            columns = ['region', 'vehicle_type', 'subsidy_amount']
            df = pd.DataFrame(data, columns=columns)
            
            if df.empty:
                return None
            
            # 컬럼명 변경
            df = df.rename(columns={
                'region': '지역',
                'vehicle_type': '차종',
                'subsidy_amount': '민간공고대수'
            })
        
        cursor.close()
        conn.close()
        return df
        
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def get_top5_models(region):
    """
    지역별 TOP5 모델 정보를 가져오는 함수
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        if region == "전체":
            # 전체 지역 TOP5 (electronic_car 테이블 사용)
            query = """
            SELECT 
                지역 as region,
                차종 as vehicle_type,
                민간공고대수 as subsidy_amount
            FROM electronic_car 
            WHERE 년도 = 2024
            ORDER BY 민간공고대수 DESC
            LIMIT 5
            """
        else:
            # 특정 지역 TOP5
            query = f"""
            SELECT 
                지역 as region,
                차종 as vehicle_type,
                민간공고대수 as subsidy_amount
            FROM electronic_car 
            WHERE 년도 = 2024 AND 지역 = '{region}'
            ORDER BY 민간공고대수 DESC
            LIMIT 5
            """
        
        cursor.execute(query)
        data = cursor.fetchall()
        columns = ['region', 'vehicle_type', 'subsidy_amount']
        df = pd.DataFrame(data, columns=columns)
        
        cursor.close()
        conn.close()
        
        if df.empty:
            return None
        
        # 순위 추가
        df['rank'] = range(1, len(df) + 1)
        
        # 컬럼명 변경
        df = df.rename(columns={
            'rank': '순위',
            'region': '지역',
            'vehicle_type': '차종',
            'subsidy_amount': '민간공고대수'
        })
        
        return df
        
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None 