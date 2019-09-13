import os
import csv


def read_local_csv_file(filename):
    local_dir = os.path.dirname(os.path.realpath(__file__))
    local_file = os.path.join(local_dir, filename)
    with open(local_file, 'r') as local_csv_file:
        reader = csv.DictReader(local_csv_file)
        for row in reader:
            yield row
