import argparse
import csv
import concurrent.futures
from benchmark_tool.query_executor import execute_query
from benchmark_tool.utils import read_csv, parse_time
import time
import hashlib
import statistics


def assign_worker(hostname, num_workers):
    """
    Assigns a worker based on the hash of the hostname.
    
    Args:
        hostname (str): The hostname for which a worker is assigned.
        num_workers (int): The number of workers available.
        
    Returns:
        int: The worker ID to which the hostname is assigned.
    """
    return int(hashlib.md5(hostname.encode()).hexdigest(), 16) % num_workers


def run_queries(concurrent_workers, query_file):
    """
    Executes queries from a CSV file using multiple concurrent workers.

    Args:
        concurrent_workers (int): The number of workers to run queries concurrently.
        query_file (str): Path to the CSV file containing hostname, start_time, and end_time values.

    Returns:
        list: A list of tuples containing (hostname, query execution time in milliseconds).
    """
    try:
        print(f"Running queries with {concurrent_workers} concurrent workers...")
        queries = read_csv(query_file)

        results = []

        # Using ThreadPoolExecutor to run queries concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            future_to_query = {}

            # Dictionary to store workers and their assigned queries
            worker_queues = {i: [] for i in range(concurrent_workers)}

            # Assign queries to workers based on hostname hash
            for query in queries:
                hostname, start_time, end_time = query

                # Assign worker based on the hostname hash
                worker_id = assign_worker(hostname, concurrent_workers)

                # Submit the query to the thread pool, and timing is moved inside
                future = executor.submit(time_query_execution, query)
                future_to_query[future] = query
                worker_queues[worker_id].append(query)

            # Collecting the results as they complete
            for future in concurrent.futures.as_completed(future_to_query):
                try:
                    hostname, execution_time = future.result()  # Get hostname and execution time
                    results.append((hostname, execution_time))  # Append the result
                except Exception as e:
                    query = future_to_query[future]
                    print(f"Error executing query for {query}: {str(e)}")

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

    # Calculate execution time in milliseconds
    execution_time = 1000 * (tok - tik)

    return hostname, execution_time


if __name__ == "__main__":
    main()
