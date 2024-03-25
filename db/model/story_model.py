from db.connection.connection import create_db_connection
from mysql.connector import Error

class StoryModel:
    def insert_fairytale_info(self, data):
        connection = create_db_connection()
        cursor = connection.cursor()
        try:
            insert_query = """INSERT INTO fairytale_info (user_code, fairytale_summary, fairytale_title, fairytale_genre, fairytale_thumb) 
            VALUES (%s, %s, %s, %s, %s)""" # %d 대신 %s 사용
            cursor.execute(insert_query, data)
            connection.commit() # DB에 변경사항을 확정합니다.
            select_query = "SELECT fairytale_code from fairytale_info WHERE fairytale_thumb = %s"
            cursor.execute(select_query, (data[4]))  # data[4]는 fairytale_thumb에 해당하는 데이터입니다.
            fairytale_code = cursor.fetchone()  # 결과가 하나만 나올 것이므로 fetchone()을 사용합니다.

            if fairytale_code:
                print("Record inserted and selected successfully.")
                return str(fairytale_code[0])  # fairytale_code를 문자열로 변환하여 리턴합니다.
            else:
                print("Record inserted but no corresponding fairytale_code found.")
                return None
        except Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()

    def insert_video_info(self, data):
        connection = create_db_connection()
        cursor = connection.cursor()
        try:
            query = "INSERT INTO fairytale_video_info (fairytale_code, video_path) VALUES (%s, %s)"
            cursor.execute(query, data)
            connection.commit()
            print("Record video successfully.")
        except Error as e:
            print(f"The error : '{e}'")
        finally:
            cursor.close()
            connection.close()