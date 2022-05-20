import os


def get_ddl_path():
    """Gets the path to the ddl file bundled with this package"""
    this_directory = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(this_directory, "cbmDefaults.ddl")
