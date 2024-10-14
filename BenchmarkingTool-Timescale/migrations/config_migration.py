from connection.db_connection import get_connection
from .create_database_schema import create_schema_and_table
from .migrate_data import load_data_from_csv


def migrate():
    try:
        CSV_FILE = "./data/cpu_usage.csv"
        conn = get_connection()
        create_schema_and_table(conn)
        load_data_from_csv(conn, CSV_FILE)
        
        print("Database setup and data import completed successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()