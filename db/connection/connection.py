import mysql.connector
from mysql.connector import Error

def create_db_connection():
    """데이터베이스 연결을 생성하고 반환합니다."""
    config = {
        'user': 'respring',
        'password': 'ReSpring3',
        'host': '192.168.0.41:3306',
        'database': 'rering',
        'raise_on_warnings': True
    }
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print("Database connection was successful")
            return connection
    except Error as e:
        print(f"The error '{e}' occurred")
