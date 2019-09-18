import os
import csv


def get_tables_dir():
    """gets the directory to the csv tables packaged with cbm_defaults

    Returns:
        str: the directory containing the packaged csv tables.
    """
    local_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(os.path.join("..", local_dir, "tables"))


def read_csv_file(filename):
    """yield rows from the specified csv stored in the csv tables dir
    returned by :py:func:`get_tables_dir`

    Args:
        filename (str): name of the csv table to read
    """
    local_file = os.path.join(get_tables_dir(), filename)
    with open(local_file, 'r') as local_csv_file:
        reader = csv.DictReader(local_csv_file)
        for row in reader:
            yield row


def get_localized_csv_file_path(filename, locale):
    filename_tokens = os.path.splitext(filename)
    return f"{filename_tokens[0]}_{locale}_{filename_tokens[1]}"
