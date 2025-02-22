import psycopg2 as pg
from dotenv import load_dotenv
import os

load_dotenv()


def connection_db():
    try:
        conn = pg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cursor = conn.cursor()
        print("Connection Successful")
        return conn, cursor  # Retorna a conexão e o cursor
    except Exception as e:
        print(f"Error: {e}")
        return None, None


if __name__ == "__main__":
    conn, cursor = connection_db()
    if conn:
        cursor.close()
        conn.close()
