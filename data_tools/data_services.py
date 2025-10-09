from common import logger

def generate_columnar_data(rows: int, cols: int) -> dict:
    """
    Generates a dictionary with columnar data.

    :param rows: Number of rows
    :param cols: Number of columns
    :return: Dictionary with column names as keys and lists of data as values
    """
    random_50_char_string = "ddgdgdgdfgdfgdfgdfgdfgdfgdfgdfgdfgdfgdfgdfg"
    data = {f"col_{i}": [f"data_{i}_{j}_{random_50_char_string}" for j in range(rows)] for i in range(cols)}
    logger.info(f"Generated columnar data with {rows} rows and {cols} columns.")
    return data

def generate_row_data(rows: int, cols: int) -> list:
    """
    Generates a list of dictionaries with row-wise data.
    :param rows: Number of rows
    :param cols: Number of columns
    :return: List of dictionaries, each representing a row of data
    """
    random_50_char_string = "ddgdgdgdfgdfgdfgdfgdfgdfgdfgdfgdfgdfgdfgdfg"
    data = [{f"col_{i}": f"data_{i}_{j}_{random_50_char_string}" for i in range(cols)} for j in range(rows)]
    logger.info(f"Generated row data with {rows} rows and {cols} columns.")
    return data