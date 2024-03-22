from db.connection.connection import create_db_connection
from mysql.connector import Error

class CloneModel:
    def update_voice_id(self, user_id: str, voice_id: str):
        print("---- [update_voice_id] ----")
        connection = create_db_connection()
        cursor = connection.cursor()
        if connection is None:
            print("Failed to connect to the database.")
            return False
        try:
            query = """
            UPDATE user_info
            SET voice_id = %s
            WHERE id = %s
            """
            cursor.execute(query, (voice_id, user_id))
            connection.commit()
            print(f"Voice ID {voice_id} was successfully updated for user {user_id}.")
            return True
        except Error as e:
            print(f"The error '{e}' occurred during the user_info table update.")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("Database connection was closed.")


    def delete_voice_id(self, voice_id: str):
        print("---- [delete_voice_id] ----")
        connection = create_db_connection()
        cursor = connection.cursor()
        if connection is None:
            print("Failed to connect to the database.")
            return False
        try:
            query = """
            DELETE 
            FROM exp_voice_id
            WHERE voice_id = %s
            """
            cursor.execute(query, (voice_id,))
            connection.commit()
            print(f"Voice ID {voice_id} was successfully deleted.")
            return True
        except Error as e:
            print(f"The error '{e}' occurred during the exp_voice_id table update.")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("Database connection was closed.")