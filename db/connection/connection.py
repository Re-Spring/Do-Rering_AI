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
        print("데이터베이스 연결 성공")
        return connection
    except Error as e:
        print(f"데이터베이스 연결 실패: '{e}'")
        raise e  # 예외를 다시 발생시켜 호출자에게 알립니다.