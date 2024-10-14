import psycopg2
import os

def get_connection():
    connection = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        host=os.getenv('DB_HOST', 'timescaledb'),
        port=os.getenv('DB_PORT', '5432')
    )
    return connection