from db.connection.connection import create_db_connection
from mysql.connector import Error

# class StoryModel:
#     def insert_story(self, data):
#         connection = create_db_connection()
#         cursor = connection.cursor()
#         try:
#             query = """INSERT INTO fairytale_info (user_code, fairytale_summary, fairytale_title, fairytale_genre, fairytale_thumb)
#             VALUES (%d, %s, %s, %s, %s)"""
#             cursor.execute(query, data)
#         except Error as e:
#             print(f"The error '{e}' occurred")
#         finally:
#             cursor.close()
#             connection.close()

class StoryModel:
    def insert_story(self, data):
        connection = create_db_connection()
        cursor = connection.cursor()
        try:
            query = """INSERT INTO fairytale_info (user_code, fairytale_summary, fairytale_title, fairytale_genre, fairytale_thumb) 
            VALUES (%s, %s, %s, %s, %s)""" # %d 대신 %s 사용
            cursor.execute(query, data)
            connection.commit() # DB에 변경사항을 확정합니다.
            print("Record inserted successfully.")
        except Error as e:
            print(f"The error '{e}' occurred")
        finally:
            cursor.close()
            connection.close()