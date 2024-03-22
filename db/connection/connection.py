import mysql.connector
from mysql.connector import Error

def create_db_connection():
    """데이터베이스 연결을 생성하고 반환합니다."""
    config = {
        'user': 'dbmasteruser',
        'password': 'A=SWadBq3MuL_V:It7>maC{y?3:J+17u',
        'host': 'ls-1cbbba9eb8cd1fd863325905431688dd6fa82dba.cfk8mckqasu6.ap-northeast-2.rds.amazonaws.com',
        'port': 3306,
        'database': 'dorering',
        'raise_on_warnings': True
    }
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("데이터베이스 연결 성공")
            return connection
    except Error as e:
        print(f"오류 '{e}' 발생")

# 컨텍스트 매니저 사용 예시
def execute_query(connection, query):
    with connection.cursor() as cursor:
        try:
            cursor.execute(query)
            connection.commit()  # 변경 사항 커밋 보장
            print("쿼리 성공적으로 실행됨")
        except Error as e:
            print(f"오류 '{e}' 발생")
