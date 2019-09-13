"""Functions for querying an MS-Access database
"""

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


def query_db(path, query, params):
    connection_string = get_connection_string(path)
    with pyodbc.connect(connection_string, autocommit=False) as connection:
        cursor = connection.cursor()
        _ = cursor.execute(query, params) if params else cursor.execute(query)
        return cursor
