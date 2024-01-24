import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings
print(settings.database_hostname)
def create_connection():
    while True:
        try:
            conn = psycopg2.connect(
            host=settings.database_hostname,
            port=settings.database_port,
            user=settings.database_username,
            password=settings.database_password,
            database=settings.database_name,
            cursor_factory=RealDictCursor
        )
            print("sucess")
            return conn
        except Exception as error:
            print("connection failed")
            print("Error",error)
            time.sleep(2)
    
conn = create_connection()
cursor = conn.cursor()
create_table_query = f"""
        CREATE TABLE IF NOT EXISTS equity_bhavcopy_data (
            id SERIAL PRIMARY KEY,
            CODE INTEGER,
            NAME VARCHAR(255),
            OPEN FLOAT,
            HIGH FLOAT,
            LOW FLOAT,
            CLOSE FLOAT,
            DATE DATE
        );
        """
create_fav_table ="""CREATE TABLE IF NOT EXISTS favourites (STOCK_ID INTEGER PRIMARY KEY);"""
cursor.execute(create_table_query)
cursor.execute(create_fav_table)
conn.commit()
conn.close()