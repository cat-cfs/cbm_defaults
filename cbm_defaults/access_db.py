"""Functions for querying the MS-Access database format
"""
import pyodbc
import contextlib


def get_connection_string(path):
    """Gets a connection string that can be used to connect to access
    databases on Windows.

    Args:
        path (str): The path to an MS access database

    Returns:
        str: a connection string for the specified database
    """
    return "Driver={Microsoft Access Driver (*.mdb, *.accdb)};" \
           f"User Id='admin';Dbq={path}"


@contextlib.contextmanager
def get_connection(path):
    """yields a connection to an ms access database at the specified path.

    Args:
        path (str): path to an ms access database
    """
    connection_string = get_connection_string(path)
    with pyodbc.connect(connection_string, autocommit=False) as connection:
        yield connection


def query_db(connection, query, params):
    cursor = connection.cursor()
    _ = cursor.execute(query, params) if params else cursor.execute(query)
    return cursor
