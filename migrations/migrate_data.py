import psycopg2
import os

def load_data_from_csv(conn, csv_file):
    try:
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"The file '{csv_file}' does not exist.")
        
        cur = conn.cursor()
        print("Loading data from CSV file using COPY...")
        
        with open(csv_file, 'r') as f:
            # Skip the header
            next(f)
            try:
                # Use COPY to insert data from CSV in one go
                cur.copy_expert("COPY cpu_usage (ts, host, usage) FROM STDIN WITH CSV", f)
            except psycopg2.Error as e:
                print(f"Error during COPY operation: {e}")
                conn.rollback()
                raise
        
        print("Data loaded successfully.")
        conn.commit()

    except FileNotFoundError as fnf_error:
        print(f"File error: {fnf_error}")
    
    except psycopg2.Error as db_error:
        print(f"Database error: {db_error}")
        conn.rollback()
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback()
    
    finally:
        try:
            cur.close()
        except Exception as close_error:
            print(f"Error closing cursor: {close_error}")
