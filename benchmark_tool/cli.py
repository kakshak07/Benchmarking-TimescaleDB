import argparse
import csv
import concurrent.futures
from benchmark_tool.query_executor import execute_query
from benchmark_tool.utils import read_csv, parse_time
import time
import hashlib
import statistics
from threading import Lock

# Locks to protect shared resources
future_to_query_lock = Lock()
worker_queues_lock = Lock()

def assign_worker(hostname, num_workers):
    """
    Assigns a worker based on the hash of the hostname.
    """
    return int(hashlib.md5(hostname.encode()).hexdigest(), 16) % num_workers

def time_query_execution(query):
    """
    Helper function to execute the query and measure the time taken.

    Args:
        query (tuple): A tuple containing (hostname, start_time, end_time).

    Returns:
        tuple: (hostname, execution time in milliseconds)
    """
    hostname, start_time, end_time = query

    # Record the start time just before executing the query
    tik = time.time()

    # Execute the query (assuming this is a synchronous blocking call)
    execute_query(query)

    # Record the end time after the query completes
    tok = time.time()
    total_time = (tok - tik) * 1000  # Convert to milliseconds

    return hostname, total_time

def run_queries(concurrent_workers, query_file):
    """
    Executes queries from a CSV file using multiple concurrent workers.
    """
    try:
        print(f"Running queries with {concurrent_workers} concurrent workers...")
        queries = read_csv(query_file)
        results = []

        # Create a separate executor for each worker
        executors = [concurrent.futures.ThreadPoolExecutor(max_workers=1) for _ in range(concurrent_workers)]

        # Dictionary to store futures for each worker
        worker_queues = {i: [] for i in range(concurrent_workers)}

        # Assign queries to workers based on hostname hash
        future_to_query = {}
        for query in queries:
            hostname, start_time, end_time = query

            # Determine the worker ID for the given hostname
            worker_id = assign_worker(hostname, concurrent_workers)

            # Submit the query to the appropriate executor
            future = executors[worker_id].submit(time_query_execution, query)
            with future_to_query_lock:
                future_to_query[future] = query
            with worker_queues_lock:
                worker_queues[worker_id].append(query)

        # Collecting the results as they complete
        for executor in executors:
            for future in concurrent.futures.as_completed(future_to_query):
                try:
                    hostname, execution_time = future.result()  # Get hostname and execution time
                    results.append((hostname, execution_time))  # Append the result
                except Exception as e:
                    query = future_to_query[future]
                    print(f"Error executing query for {query}: {str(e)}")

        # Shutdown all executors
        for executor in executors:
            executor.shutdown()

        return results

    except FileNotFoundError:
        print(f"Error: The file {query_file} was not found.")
        return []
    except csv.Error as e:
        print(f"Error reading CSV file {query_file}: {str(e)}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return []

def main():
    """
    The main function parses arguments, runs the benchmark, and calculates statistics.
    """
    parser = argparse.ArgumentParser(description="Benchmark TimescaleDB Queries.")
    parser.add_argument('query_file', type=str, help="Path to the CSV file containing query parameters.")
    parser.add_argument('--workers', type=int, default=3, help="Number of concurrent workers.")

    args = parser.parse_args()
    query_file = args.query_file
    workers = args.workers

    try:
        print(f"Starting benchmark with {workers} concurrent workers...")
        q_ts = run_queries(workers, query_file)

        if not q_ts:
            print("No queries were processed. Exiting.")
            return

        print("Calculating statistics...")
        execution_times = [execution_time for _, execution_time in q_ts]

        result = {
            'total_queries': len(execution_times),
            'total_time': sum(execution_times),
            'min_time': min(execution_times),
            'max_time': max(execution_times),
            'avg_time': sum(execution_times) / len(execution_times),
            'median_time': statistics.median(execution_times)
        }

        print(result)

    except Exception as e:
        print(f"An error occurred during benchmarking: {str(e)}")

if __name__ == "__main__":
    main()
