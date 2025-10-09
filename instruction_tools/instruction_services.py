from common import logger

PSQL_RTITSQL_INSTRUCTIONS = """
# Instructions to rewrite a P-SQL query to T-SQL for RTI
1. Use `kusto_known_services` to connect to the known RTI services.
2. Replace the table names with corresponding materialized views from `postgre-rti-table-mapping.csv`. Validate the result once editing is done. Use TODO list to keep track of the tasks.
3. Replace column name `UHID` with `uhid`.
4. Change the syntax from P-SQL to T-SQL. Once done, ensure that nothing else is modified. Plan your steps and use TODO list to keep track of the tasks. 
5. Change the order of joins such that the table or CTE with UHID filter is first. For this, identify the filters in the WHERE clause and move the corresponding tables to the front. Use TODO list to keep track of the tasks.
6. Replace CTEs with corresponding sub queries. For this first identify the aliases and replace one by one. Do not worry about repeated use of same query. Keep track of the steps using TODO list.
7. Use the `kusto_tsql_query` tool to validate the syntax of resulting query. If the query results in any error, correct and retry.
8. If the query is exhausting the resources after all the steps above, Stop.
"""

def get_instructions_convert_psql_to_rtitsql(rows: int, cols: int) -> str:
    """
    Fetches the instructions to convert PostgreSQL queries to Fabric RTI T-SQL.

    :return: Instructions as a markdown string
    """
    return PSQL_RTITSQL_INSTRUCTIONS
