import csv
from datetime import datetime

def read_csv(file_path):
    queries = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            hostname, start_time, end_time = row
            queries.append((hostname, parse_time(start_time), parse_time(end_time)))
    return queries

def parse_time(time_str):
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
