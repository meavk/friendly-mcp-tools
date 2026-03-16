import os
import re
import time
from contextlib import contextmanager
from typing import Any, Dict, Iterable, Iterator, List

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

from common import logger

load_dotenv()

READ_QUERY_PATTERN = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)
WRITE_QUERY_PATTERN = re.compile(r"^\s*(insert|update|delete)\b", re.IGNORECASE)
FORBIDDEN_WRITE_PATTERN = re.compile(
    r"\b(create|alter|drop|truncate|grant|revoke|vacuum|analyze|comment|refresh|call|do|copy|merge)\b",
    re.IGNORECASE,
)
FORBIDDEN_CONTROL_PATTERN = re.compile(
    r"\b(begin|start\s+transaction|commit|rollback|savepoint|release\s+savepoint|set\b|show\b)\b",
    re.IGNORECASE,
)

postgres_connection_string = os.getenv("POSTGRES_CONNECTION_STRING")
postgres_connection_pool: ConnectionPool | None = None


def _is_postgres_configured() -> bool:
    return bool(postgres_connection_string)


def _ensure_postgres_configured() -> None:
    if not _is_postgres_configured():
        raise ValueError(
            "POSTGRES_CONNECTION_STRING must be set in environment variables or .env file"
        )


def _get_pool() -> ConnectionPool:
    global postgres_connection_pool

    _ensure_postgres_configured()
    if postgres_connection_pool is None:
        postgres_connection_pool = ConnectionPool(
            conninfo=postgres_connection_string,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        postgres_connection_pool.open()
    return postgres_connection_pool


def _contains_multiple_statements(query: str) -> bool:
    statements = [segment.strip() for segment in query.split(";") if segment.strip()]
    return len(statements) > 1 or query.strip().endswith(";")


def _validate_read_query(query: str) -> None:
    if _contains_multiple_statements(query):
        raise ValueError("Read queries must contain exactly one statement and must not end with a semicolon")

    if not READ_QUERY_PATTERN.match(query):
        raise ValueError("Only SELECT and WITH read queries are allowed")

    if FORBIDDEN_WRITE_PATTERN.search(query) or FORBIDDEN_CONTROL_PATTERN.search(query):
        raise ValueError("Read queries may not contain write, DDL, or transaction-control statements")


def _validate_write_query(query: str) -> None:
    if _contains_multiple_statements(query):
        raise ValueError("Write queries must contain exactly one statement and must not end with a semicolon")

    if not WRITE_QUERY_PATTERN.match(query):
        raise ValueError("Only INSERT, UPDATE, and DELETE statements are allowed")

    if FORBIDDEN_WRITE_PATTERN.search(query) or FORBIDDEN_CONTROL_PATTERN.search(query):
        raise ValueError("Write queries may not contain DDL or transaction-control statements")


@contextmanager
def _get_connection() -> Iterator[Any]:
    with _get_pool().connection() as connection:
        yield connection


def _normalize_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized_rows: List[Dict[str, Any]] = []
    for row in rows:
        normalized_rows.append(dict(row))
    return normalized_rows


def _execute_query(query: str, fetch_results: bool) -> Dict[str, Any]:
    start_time = time.time()
    logger.info(f"Running PostgreSQL query:\n{query}")

    with _get_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)

                results: List[Dict[str, Any]] = []
                if fetch_results:
                    fetched_rows = cursor.fetchall()
                    results = _normalize_rows(fetched_rows)

                row_count = len(results) if fetch_results else cursor.rowcount

            if fetch_results:
                connection.rollback()
            else:
                connection.commit()
        except Exception:
            connection.rollback()
            raise

    elapsed_seconds = time.time() - start_time
    logger.info(f"PostgreSQL query executed in {elapsed_seconds:.2f} seconds")

    response: Dict[str, Any] = {
        "elapsed_seconds": elapsed_seconds,
    }
    if fetch_results:
        response["results"] = results
        response["row_count"] = row_count
    else:
        response["rows_affected"] = row_count
    return response


def run_warmup_query() -> None:
    _get_pool()
    _execute_query("SELECT 1", fetch_results=True)
    logger.info("PostgreSQL connection initialized, warmup query executed.")


def postgresql_read_query(query: str) -> Dict[str, Any]:
    """
    Execute a read-only PostgreSQL query.

    :param query: SQL read query. Only SELECT and WITH statements are allowed.
    :return: Dictionary with results, row count, and elapsed time in seconds.

    Example:
        >>> result = postgresql_read_query("SELECT 1 AS value")
        >>> result
        {'results': [{'value': 1}], 'row_count': 1, 'elapsed_seconds': 0.12}
    """
    _validate_read_query(query)
    return _execute_query(query, fetch_results=True)


def postgresql_write_query(query: str) -> Dict[str, Any]:
    """
    Execute a guarded PostgreSQL write query.

    :param query: SQL write query. Only INSERT, UPDATE, and DELETE statements are allowed.
    :return: Dictionary with affected row count and elapsed time in seconds.

    Example:
        >>> result = postgresql_write_query("UPDATE widgets SET enabled = false WHERE id = 10")
        >>> result
        {'rows_affected': 1, 'elapsed_seconds': 0.08}
    """
    _validate_write_query(query)
    return _execute_query(query, fetch_results=False)
