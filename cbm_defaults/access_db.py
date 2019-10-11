"""Functions for querying the MS-Access database format
"""
import contextlib
import pyodbc


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
    """Run the specified query with parameters on the specified connection.

    Args:
        connection (object): a connection to an ms access database
        query (str): ms access query
        params (iterable): query parameters

    Returns:
        cursor: the iterable cursor with the query result
    """
    # Make a new cursor #
    cursor = connection.cursor()
    # Documented issue with pyodbc #
    # See stackoverflow.com/questions/20240130 #
    if params:
        params = tuple(float(x) if type(x) is int else x for x in params)
    # Execute #
    cursor.execute(query, params) if params else cursor.execute(query)
    # Return #
    return cursor
