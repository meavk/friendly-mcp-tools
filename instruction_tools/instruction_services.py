from common import logger

PSQL_RTITSQL_INSTRUCTIONS = """
# Instructions to rewrite a P-SQL query to T-SQL for RTI
1. Replace the table names with corresponding materialized views from `postgre-rti-table-mapping.csv`. Validate the result once editing is done. Use TODO list to keep track of the tasks.
2. Replace column name `UHID` with `uhid`. Also convert all column names to lower case as that's the convention followed in RTI.
3. Change the syntax from P-SQL to T-SQL. Once done, ensure that nothing else is modified. Plan your steps and use TODO list to keep track of the tasks. 
4. Change the order of joins such that the table or CTE with UHID filter is first. For this, identify the filters in the WHERE clause and move the corresponding tables to the front. Use TODO list to keep track of the tasks.
5. Replace CTEs with corresponding sub queries. For this first identify the aliases and replace one by one. Do not worry about repeated use of same query. Keep track of the steps using TODO list.
6. Use the `fabric_rti_run_query_and_count_records` tool to validate the syntax of resulting query. If the query results in any error, correct and retry.
7. If the query is exhausting the resources after all the steps above, Stop.
8. If the query results in no records, query the relevant tables and find a UHID that has data. Use that UHID to validate the query.
"""

def get_instructions_convert_psql_to_rtitsql(rows: int, cols: int) -> str:
    """
    Fetches the instructions to convert PostgreSQL queries to Fabric RTI T-SQL.

    :return: Instructions as a markdown string
    """
    return PSQL_RTITSQL_INSTRUCTIONS
