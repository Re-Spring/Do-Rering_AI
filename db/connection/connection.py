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
            print("Database connection was successful")
            return connection
    except Error as e:
        print(f"The error '{e}' occurred")
