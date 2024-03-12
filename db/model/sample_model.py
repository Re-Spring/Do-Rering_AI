# story_model.py

from db.connection.connection import create_db_connection
from mysql.connector import Error

def insert_record(data):
    connection = create_db_connection()
    cursor = connection.cursor()
    try:
        query = "INSERT INTO your_table (column1, column2) VALUES (%s, %s)"
        cursor.execute(query, data)
        connection.commit()
        print("Record inserted successfully.")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()
        connection.close()

def read_records():
    connection = create_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM your_table")
        results = cursor.fetchall()
        for row in results:
            print(row)
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()
        connection.close()

def update_record(data):
    connection = create_db_connection()
    cursor = connection.cursor()
    try:
        query = "UPDATE your_table SET column1 = %s WHERE column2 = %s"
        cursor.execute(query, data)
        connection.commit()
        print("Record updated successfully.")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()
        connection.close()

def delete_record(data):
    connection = create_db_connection()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM your_table WHERE column2 = %s"
        cursor.execute(query, data)
        connection.commit()
        print("Record deleted successfully.")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()
        connection.close()

# 여기에 update_record()와 delete_record() 함수를 추가할 수 있습니다.

