import os
from dotenv import load_dotenv

load_dotenv()

# Helper function to parse boolean from environment variables
def getenv_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() == "true"

# Server configuration
SERVER_NAME = "Friendly MCP Tools"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
HTTP_PATH = "/mcp"
STATELESS_HTTP = True

# Service feature flags (default to False for safety)
ENABLE_DATA_TOOLS = getenv_bool("ENABLE_DATA_TOOLS")
ENABLE_FABRIC_RTI_TOOLS = getenv_bool("ENABLE_FABRIC_RTI_TOOLS")
ENABLE_GIT_CLI_TOOLS = getenv_bool("ENABLE_GIT_CLI_TOOLS")
ENABLE_INSTRUCTION_TOOLS = getenv_bool("ENABLE_INSTRUCTION_TOOLS")