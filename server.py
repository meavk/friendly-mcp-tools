from mcp.server.fastmcp import FastMCP
from tools import register_tools, initialize_tools
import config
import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run the FastMCP server.")
	parser.add_argument("--port", type=int, default=config.DEFAULT_PORT, help="Port to listen on (default: 8000)")
	args = parser.parse_args()

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
