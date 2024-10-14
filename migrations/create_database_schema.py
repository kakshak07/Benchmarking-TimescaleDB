def create_schema_and_table(conn):
    commands = [
        "CREATE EXTENSION IF NOT EXISTS timescaledb;",
        """
        CREATE TABLE IF NOT EXISTS cpu_usage (
            ts    TIMESTAMPTZ,
            host  TEXT,
            usage DOUBLE PRECISION
        );
        """,
        "SELECT create_hypertable('cpu_usage', 'ts', if_not_exists => TRUE);"
    ]
    cur = conn.cursor()
    print("Creating schema and table...")
    for command in commands:
        cur.execute(command)

    print("Schema and table created successfully.")
    conn.commit()
    cur.close()