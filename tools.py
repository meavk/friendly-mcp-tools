from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from data_tools import data_services
from instruction_tools import instruction_services
from fabric_rti_tools import fabric_rti_services

def initialize_tools() -> None:
    fabric_rti_services.run_warmup_query()

def register_tools(mcp: FastMCP) -> None:
    mcp.add_tool(
        data_services.generate_columnar_data,
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
    )
    
    mcp.add_tool(
        data_services.generate_row_data,
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
    )

    mcp.add_tool(
        instruction_services.get_instructions_convert_psql_to_rtitsql,
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
    )

    mcp.add_tool(
        fabric_rti_services.fabric_rti_run_query_and_count_records,
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
    )
