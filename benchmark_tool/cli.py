import argparse
import csv
import concurrent.futures
from benchmark_tool.query_executor import execute_query
from benchmark_tool.utils import read_csv, parse_time
import time
import statistics

def run_queries(concurrent_workers, query_file):
    """
    Executes queries from a CSV file using multiple concurrent workers.
    
    Args:
        concurrent_workers (int): The number of workers to run queries concurrently.
        query_file (str): Path to the CSV file containing hostname, start_time, and end_time values.
    
    Returns:
        list: A list of query execution times in milliseconds.
    """
    try:
        print(f"Running queries with {concurrent_workers} concurrent workers...")
        queries = read_csv(query_file)
        
        # Create a mapping of hostname to a worker
        hostname_to_worker = {}
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            future_to_query = {}
            for query in queries:
                hostname, start_time, end_time = query
                
                if hostname not in hostname_to_worker:
                    worker_id = len(hostname_to_worker) % concurrent_workers
                    hostname_to_worker[hostname] = worker_id
                
                worker_id = hostname_to_worker[hostname]
                future = executor.submit(execute_query, query)
                future_to_query[future] = (worker_id, query)
            
            # Collecting the results as they are completed
            for future in concurrent.futures.as_completed(future_to_query):
                tik = time.time()  # Start time
                try:
                    query_result = future.result()
                    results.append(1000 * (time.time() - tik))  # Execution time in ms
                except Exception as e:
                    query = future_to_query[future][1]
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
    parser.add_argument('--workers', type=int, default=4, help="Number of concurrent workers.")
    
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

        result = {
            'total_queries': len(q_ts),
            'total_time': sum(q_ts),
            'min_time': min(q_ts),
            'max_time': max(q_ts),
            'avg_time': sum(q_ts) / len(q_ts),
            'median_time': statistics.median(q_ts)
        }
        print(result)
        
    except Exception as e:
        print(f"An error occurred during benchmarking: {str(e)}")

if __name__ == "__main__":
    main()
