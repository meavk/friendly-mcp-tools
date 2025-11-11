from typing import Dict, Any
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties, response as KustoResponse
import concurrent.futures
import time
import os
from dotenv import load_dotenv
from common import logger

load_dotenv()

cluster = os.getenv("CLUSTER_URL")
database = os.getenv("DATABASE_NAME")

if not cluster or not database:
    raise ValueError("CLUSTER_URL and DATABASE_NAME must be set in environment variables or .env file")

kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(cluster)
client = KustoClient(kcsb)

def _count_columnar_records(columnar_data: Dict[str, Any]) -> int:
    if 'data' not in columnar_data or not columnar_data['data']:
        return 0
    
    # Get the first column and count its length
    first_column = next(iter(columnar_data['data'].values()))
    return len(first_column)

def _detect_query_language(query: str) -> str:
    lines = query.lstrip().splitlines()
    if lines and lines[0].strip() == "--":
        return "sql"
    return "kql"

def _run_query(query: str, query_language: str = None) -> tuple[list, float]:
    start_time = time.time()
    properties = ClientRequestProperties()
    query_language = query_language or _detect_query_language(query)
    properties.set_option("query_language", query_language)
    logger.info(f"Running {query_language} Query:\n{query}")
    result_set = client.execute(database, query, properties)
    end_time = time.time()
    elapsed_seconds = end_time - start_time
    results_dict = result_set.primary_results[0].to_dict()['data']
    logger.info(f"Query executed in {elapsed_seconds:.2f} seconds")
    return (results_dict, elapsed_seconds)

def run_warmup_query():
    _run_query("SELECT 1", "sql")
    logger.info("Kusto connection initialized, warmup query executed.")

def fabric_rti_run_query_and_count_records(query: str, query_language: str = None) -> Dict[str, Any]:
    """
    Runs a KQL or T-SQL against the Fabric RTI database and counts the number of records returned.
    Also returns the elapsed time for the query execution.
    
    :param query: The query string to execute
    :param query_language: Optional, specify 'sql' or 'kql'. If None, it will be auto-detected. A '--' in the first line indicates 'sql'.
    :return: Dictionary with record count and elapsed time in seconds
    
    Example:
        >>> result = run_query_and_count_records("SELECT TOP 10 * FROM MyTable", "sql")
        >>> result
        {'record_count': 10, 'elapsed_seconds': 1.23}
    """
    result = _run_query(query, query_language)
    (data, elapsed_seconds) = result
    record_count = len(data) if data and isinstance(data, list) else 0
    logger.info(f"Query returned {record_count} records.")
    return { "record_count": record_count, "elapsed_seconds": elapsed_seconds }

def fabric_rti_run_query_and_get_results(query: str, query_language: str = None) -> Dict[str, Any]:
    """
    Runs a KQL or T-SQL against the Fabric RTI database and returns the results.
    Also returns the elapsed time for the query execution.
    
    :param query: The query string to execute
    :param query_language: Optional, specify 'sql' or 'kql'. If None, it will be auto-detected. A '--' in the first line indicates 'sql'.
    :return: Dictionary with the results and elapsed time in seconds
    
    Example:
        >>> result = run_query_and_get_results("SELECT TOP 10 * FROM MyTable", "sql")
        >>> result
        {'results': [...], 'elapsed_seconds': 1.23}
    """


    result = _run_query(query, query_language)
    (data, elapsed_seconds) = result
    record_count = len(data) if data and isinstance(data, list) else 0
    logger.info(f"Query returned {record_count} records.")
    return { "results": data, "elapsed_seconds": elapsed_seconds }

def fabric_rti_get_materialized_view_schema(materialized_view_name: str) -> Dict[str, Any]:
    """
    Gets the schema of a materialized view in the Fabric RTI database.
    
    :param materialized_view_name: The name of the materialized view
    :return: Dictionary with column name and it's type in results and elapsed time in seconds
    
    Example:
        >>> result = run_query_and_get_results("SELECT TOP 10 * FROM MyTable", "sql")
        >>> result
        {'results': [...], 'elapsed_seconds': 1.23}
    """
    mv_schema_query = f"""
.show materialized-view {materialized_view_name} schema as json 
| project mv_schema = todynamic(Schema).OrderedColumns
| mv-expand mv_schema
| project ColumnName = tostring(mv_schema.Name), ColumnType = tostring(mv_schema.Type)
| order by ColumnName asc 
"""

    result = _run_query(mv_schema_query, "kql")
    (data, elapsed_seconds) = result
    record_count = len(data) if data and isinstance(data, list) else 0
    logger.info(f"Query returned {record_count} columns.")
    return { "results": data, "elapsed_seconds": elapsed_seconds }