import mysql.connector
from dotenv import load_dotenv
import os
import time

load_dotenv()

def mysql_operations():
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
    }
    print(db_config)
    # 接続再試行用
    for _ in range(30):
        try:
            conn = mysql.connector.connect(**db_config)
            break
        except mysql.connector.Error:
            time.sleep(1)
    else:
        print("データベースへの接続に失敗しました")
        return

    cur = conn.cursor()

    cur.execute("SELECT 'Hello from MySQL via Python + uv!'")
    print(cur.fetchone())

    cur.close()
    conn.close()

if __name__ == "__main__":
    print("Hello from calendar-db!")
    mysql_operations()