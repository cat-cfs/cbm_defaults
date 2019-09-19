"""Methods for creating and adding data to a cbm_defaults database
"""
import os
import contextlib
import logging
import sqlite3


def create_database(sqlite_path):
    """Create a blank sqlite database at the specified path.

    Args:
        sqlite_path (str): path to the new blank sqlite database.

    Raises:
        ValueError: the specified path already exists
    """
    if os.path.exists(sqlite_path):
        raise ValueError(
            f"specified path already exists {sqlite_path}")
    with get_connection(sqlite_path) as _:
        return


@contextlib.contextmanager
def get_connection(sqlite_path):
    """yields a connection to a sqlite database at the specified path.

    Args:
        sqlite_path (str): path to a sqlite database
    """
    logging.info("opening %s", sqlite_path)
    with sqlite3.connect(sqlite_path) as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        yield conn
        logging.info("closing %s", sqlite_path)


def execute_ddl_file(ddl_path, sqlite_path):
    """Execute the semicolon delimited sqlite data definition (DDL) statements
    in the specified *ddl_path* on the database at the specified sqlite_path.

    Args:
        ddl_path (str): path to a file containing semicolon delimited sqlite
            DDL statements.
        sqlite_path (str): path to a sqlite database on which the statements
            will be run.
    """
    with get_connection(sqlite_path) as conn, \
            open(ddl_path, 'r') as ddl_file:

        ddl_statements = [
            x for x in ddl_file.read().split(";") if x is not None]
        cursor = conn.cursor()
        for ddl in ddl_statements:
            cursor.execute(ddl)


def add_record(connection, table_name, **kwargs):
    """Add a record to the specified table in the connected database with
    the column name, row value pairs specified by keyword args

    Args:
        connection (sqlite3.Connection): a connection to an sqlite database
        table_name (str): the name of the table to which the record is added
    """
    col_list = kwargs.keys()

    query = "INSERT INTO {table_name} ({col_list}) VALUES ({values})" \
        .format(
            table_name=table_name,
            col_list=",".join(col_list),
            values=",".join(["?"]*len(col_list))
        )
    params = [kwargs[k] for k in col_list]
    cursor = connection.cursor()
    cursor.execute(query, params)
