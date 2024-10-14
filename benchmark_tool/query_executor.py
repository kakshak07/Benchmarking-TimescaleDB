import psycopg2
from connection.db_connection import get_connection
from .utils import parse_time

# Query template to retrieve CPU usage statistics by minute
QUERY_TEMPLATE = """
SELECT
    date_trunc('minute', ts) AS minute,
    MIN(usage) AS min_usage,
    MAX(usage) AS max_usage
FROM cpu_usage
WHERE host = %s
AND ts BETWEEN %s AND %s
GROUP BY minute;
"""

def execute_query(query_params):
    """
    Executes a SQL query to retrieve the minimum and maximum CPU usage per minute 
    for a specific host and time range.

    Args:
        query_params (tuple): A tuple containing hostname, start_time, and end_time values.

    Returns:
        list: A list of rows containing the minute, min_usage, and max_usage data.
    """
    hostname, start_time, end_time = query_params
    conn = None
    
    try:
        # Establishing the database connection
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(QUERY_TEMPLATE, (hostname, start_time, end_time))
            rows = cur.fetchall()
            return rows
    except psycopg2.DatabaseError as db_error:
        print(f"Database error occurred while executing query for host {hostname}: {str(db_error)}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while executing query for host {hostname}: {str(e)}")
        return []
    finally:
        # Ensure the connection is closed even if an error occurs
        if conn is not None:
            conn.close()
