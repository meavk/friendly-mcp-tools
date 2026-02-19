from mcp.server.fastmcp import FastMCP
from tools import register_tools, initialize_tools
import config
import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run the FastMCP server.")
	parser.add_argument("--port", type=int, default=config.DEFAULT_PORT, help="Port to listen on (default: 8000)")
	args = parser.parse_args()

	# Log enabled services
	enabled_services = []
	if config.ENABLE_DATA_TOOLS:
		enabled_services.append("data_tools")
	if config.ENABLE_FABRIC_RTI_TOOLS:
		enabled_services.append("fabric_rti_tools")
	if config.ENABLE_GIT_CLI_TOOLS:
		enabled_services.append("git_cli_tools")
	if config.ENABLE_INSTRUCTION_TOOLS:
		enabled_services.append("instruction_tools")
	
	print(f"Starting {config.SERVER_NAME}...")
	print(f"Enabled services: {', '.join(enabled_services) if enabled_services else 'None'}")

	server = FastMCP(
		name=config.SERVER_NAME,
		host=config.DEFAULT_HOST,
		port=args.port,
		streamable_http_path=config.HTTP_PATH,
		stateless_http=config.STATELESS_HTTP,
    )
	
	initialize_tools()
	register_tools(server)
	server.run(transport="streamable-http")
