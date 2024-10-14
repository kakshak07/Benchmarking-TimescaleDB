import psycopg2
import os
import time

def get_connection():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password'),
            host=os.getenv('DB_HOST', 'timescaledb'),
            port=os.getenv('DB_PORT', '5432')
        )
        connection.close()  # Close the connection if it succeeds
        return True
    except psycopg2.OperationalError:
        return False

if __name__ == "__main__":
    if get_connection():
        print("Database is ready!")
        exit(0)
    else:
        exit(1)
