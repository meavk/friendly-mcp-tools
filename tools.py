from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
import config


def initialize_tools() -> None:
    """Initialize services that require warmup/setup"""
    if config.ENABLE_FABRIC_RTI_TOOLS:
        from fabric_rti_tools import fabric_rti_services
        fabric_rti_services.run_warmup_query()


def register_tools(mcp: FastMCP) -> None:
    """Register tools based on enabled services"""
    
    if config.ENABLE_DATA_TOOLS:
        from data_tools import data_services
        
        mcp.add_tool(
            data_services.generate_columnar_data,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
        
        mcp.add_tool(
            data_services.generate_row_data,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
    
    if config.ENABLE_INSTRUCTION_TOOLS:
        from instruction_tools import instruction_services
        
        mcp.add_tool(
            instruction_services.get_instructions_convert_psql_to_rtitsql,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
    
    if config.ENABLE_FABRIC_RTI_TOOLS:
        from fabric_rti_tools import fabric_rti_services
        
        mcp.add_tool(
            fabric_rti_services.fabric_rti_run_query_and_count_records,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
        
        mcp.add_tool(
            fabric_rti_services.fabric_rti_get_materialized_view_schema,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
    
    if config.ENABLE_GIT_CLI_TOOLS:
        from git_cli_tools import git_cli_services
        
        mcp.add_tool(
            git_cli_services.git_issue_list,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
        
        mcp.add_tool(
            git_cli_services.git_issue_view,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
        
        mcp.add_tool(
            git_cli_services.git_pr_list,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
        
        mcp.add_tool(
            git_cli_services.git_pr_view,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )
        
        mcp.add_tool(
            git_cli_services.git_pr_diff,
            annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
        )