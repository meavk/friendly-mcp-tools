import re
from typing import Dict, Any, List
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties, response as KustoResponse
import concurrent.futures
import time
import os
from dotenv import load_dotenv
from common import logger
import json

load_dotenv()

cluster = os.getenv("CLUSTER_URL")
database = os.getenv("DATABASE_NAME")
client_id = os.getenv("KUSTO_CLIENT_ID")
client_secret = os.getenv("KUSTO_CLIENT_SECRET")
tenant_id = os.getenv("KUSTO_TENANT_ID")

if not cluster or not database:
    raise ValueError("CLUSTER_URL and DATABASE_NAME must be set in environment variables or .env file")

if client_id and client_secret and tenant_id:
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
        cluster, client_id, client_secret, tenant_id
    )
else:
    kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(cluster)
client = KustoClient(kcsb)

def get_resource_comsumption(tables: List[KustoResponse.KustoResultTable], query_index: int = 0) -> Dict[str, Any]:
    query_info_tables = [t for t in tables if t.table_kind == "QueryCompletionInformation"]
    query_info = query_info_tables[query_index] if len(query_info_tables) > query_index else None
    if query_info:
        query_info_data = query_info.to_dict()['data']
        resource_consumptions = [d for d in query_info_data if d['EventTypeName'] == "QueryResourceConsumption" ]
        if resource_consumptions:
            payload_string = resource_consumptions[0]['Payload']
            try:
                payload = json.loads(payload_string)
                return payload
            except (TypeError, json.JSONDecodeError):
                return None
    return None

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
    resource_comsumption = get_resource_comsumption(result_set.tables)
    results_dict = result_set.primary_results[0].to_dict()['data']
    logger.info(f"Query executed in {elapsed_seconds:.2f} seconds")
    return (results_dict, elapsed_seconds, resource_comsumption)

def _return_query_results(result: tuple[list, float, Dict[str, Any]], only_count=False) -> Dict[str, Any]:
    data, elapsed_seconds, resource_comsumption = result
    record_count = len(data) if data and isinstance(data, list) else 0
    logger.info(f"Query returned {record_count} records.")
    if only_count:
        return { "record_count": record_count, "elapsed_seconds": elapsed_seconds, "resource_consumption": resource_comsumption }
    return { "results": data, "elapsed_seconds": elapsed_seconds, "resource_consumption": resource_comsumption }

def run_warmup_query():
    _run_query("SELECT 1", "sql")
    logger.info("Kusto connection initialized, warmup query executed.")

def fabric_rti_run_query_and_count_records(query: str, query_language: str = None) -> Dict[str, Any]:
    """
    Runs a KQL or T-SQL against the Fabric RTI database and counts the number of records returned.
    Also returns the elapsed time for the query execution.
    
    :param query: The query string to execute
    :param query_language: Optional, specify 'sql' or 'kql'. If None, it will be auto-detected. A '--' in the first line indicates 'sql'.
    :return: Dictionary with record count, elapsed time in seconds and resource consumption.
    
    Example:
        >>> result = run_query_and_count_records("SELECT TOP 10 * FROM MyTable", "sql")
        >>> result
        {'record_count': 10, 'elapsed_seconds': 1.23, 'resource_consumption': {...}}
    """
    result = _run_query(query, query_language)
    return _return_query_results(result, only_count=True)

def fabric_rti_run_query_and_get_results(query: str, query_language: str = None) -> Dict[str, Any]:
    """
    Runs a KQL or T-SQL against the Fabric RTI database and returns the results.
    Also returns the elapsed time for the query execution.
    
    :param query: The query string to execute
    :param query_language: Optional, specify 'sql' or 'kql'. If None, it will be auto-detected. A '--' in the first line indicates 'sql'.
    :return: Dictionary with the results, elapsed time in seconds, and resource consumption.
    
    Example:
        >>> result = run_query_and_get_results("SELECT TOP 10 * FROM MyTable", "sql")
        >>> result
        {'results': [...], 'elapsed_seconds': 1.23, 'resource_consumption': {...}}
    """
    result = _run_query(query, query_language)
    return _return_query_results(result)

def fabric_rti_get_schema(kql_query_or_object: str) -> Dict[str, Any]:
    """
    Gets the schema of a table, materialized view, or KQL query result.
    
    :param kql_query_or_object: The KQL query or object to get the schema for
    :return: Dictionary with column name, ordinal, data type and ColumnType in results, elapsed time in seconds, and resource consumption.
    
    Example:
        >>> result = fabric_rti_get_schema("MyMaterializedView")
        >>> result
        {'results': [...], 'elapsed_seconds': 1.23, 'resource_consumption': {...}}
    """
    mv_schema_query = f"""
{kql_query_or_object}
| getschema
"""
    result = _run_query(mv_schema_query, "kql")
    return _return_query_results(result)