# TimescaleDB Benchmarking Tool

## Overview
This project provides a Python-based command-line tool to benchmark SELECT query performance across multiple workers against a TimescaleDB instance. The tool takes a CSV file with query parameters and executes queries concurrently using a worker pool. Each worker processes queries for specific hostnames, ensuring consistency and concurrency. The results are aggregated to provide key performance statistics, including of queries run, the total processing time across all queries, the minimum query time (for a single query), the median query time, the average query time, and the maximum query time..



## Installation Steps

1. **Clone the repository:**
   ```bash
   git@github.com:kakshak07/Benchmarking-TimescaleDB.git

2. **cd into the folder** 
   ```bash
   cd Benchmarking-TimescaleDB
3. **Run this, if you run without -d it will not dettac from terminal and by default you will see output for total worker 3 as default** 
   ```bash
   docker compose -f docker-compose.yml up -d --build
4. **Enter into the service container** 
   ```bash
   docker compose exec python_service /bin/bash

4. **Now you are inside the service container, now data will already be present since the migration script is completed successfully, now modify the worker thread to get the output results** 
   ```bash
   python -m benchmark_tool.cli data/query_params.csv --workers 3

### Though process and implementation details
The overall approach centers on implementing a consistent hashing mechanism strategy to efficiently allocate queries to workers, ensuring minimal overhead and ensuring the same worker processes queries for a given hostname across multiple query executions. This design ensures locality of data, optimizes cache utilization, and prevents redundant connections to the TimescaleDB instance, leading to better performance.


**Worker Management and Concurrent Query Execution:** Given the need for concurrent processing, the number of workers is specified dynamically, and each worker operates in its own thread or process. By employing a hashmap strategy, queries are distributed to workers based on the hostname. This mapping is critical since queries for the same hostname need to be consistently processed by the same worker for better performance and query locality.

The worker mapping can be visualized as:

Hashmap (hashing_function(hostname) → worker): A simple hashing function is applied to the hostname, determining which worker should handle queries associated with that hostname. This avoids random assignment and guarantees a stable worker-hostname relationship across queries.


**Summary Report Generation:** After all queries are processed, the tool outputs a comprehensive report with the following statistics:

Total number of queries processed across all workers.
Total time spent processing queries.
Minimum, median, average, and maximum query times. This data helps determine the overall efficiency of the system, identifying bottlenecks in query processing or database performance.

**Dockerization and Automation:** The entire benchmarking tool, including TimescaleDB setup and worker management, is containerized using Docker Compose. This ensures the tool can be easily deployed, with all dependencies encapsulated, allowing for easy integration, testing, and reusability. Docker ensures that workers and the database run in isolated environments, avoiding conflicts.


The provided Docker Compose configuration sets up a `timescaledb` service, utilizing the latest TimescaleDB image with PostgreSQL 16, and a `python_service` that depends on it. The `timescaledb` container is configured with a health check to ensure it's ready before the Python service starts, which mounts the current directory to allow access to the application code and relevant files. When the `python_service` runs, it first executes a script (`health_check_db.py`) to confirm the database is available. Upon successful connection, it initiates the configuration migration (`migrations.config_migration`) and subsequently launches the benchmarking tool, using parameters defined in `data/query_params.csv` with a specified number of worker processes. This sequence not only ensures that the application is properly connected to the database but also guarantees that the configuration migration is executed, leading to updated migration records being saved.

# Benchmark Results
The results may vary depending on the implementation language, the hashing function used for assigning workers to nodes, and other factors. An increase in the number of collisions could potentially lead to longer execution times.

Results are in milli seconds:

| Workers | Total Queries | Total Time (ms) | Min Time (ms) | Max Time (ms) | Avg Time (ms) | Median Time (ms) |
|---------|---------------|----------------|--------------|--------------|--------------|-----------------|
| 1       | 200           | 1.0362         | 0.0014       | 0.0496       | 0.0052       | 0.0033          |
| 2       | 200           | 0.6139         | 0.0005       | 0.0534       | 0.0031       | 0.0024          |
| 3       | 200           | 0.7131         | 0.0005       | 0.0238       | 0.0036       | 0.0026          |
| 4       | 200           | 0.6838         | 0.0005       | 0.1438       | 0.0034       | 0.0021          |
| 5       | 200           | 1.5371         | 0.0005       | 0.7634       | 0.0077       | 0.0024          |


**Notes:**
- All times are measured in milliseconds (ms).
- Each benchmark was conducted with 200 queries.