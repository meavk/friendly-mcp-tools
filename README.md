# Friendly MCP Tools

A collection of tools to interact with Microsoft Fabric RTI databases, PostgreSQL databases, and other utility services.

> Warning: Use read-only credentials wherever possible. PostgreSQL write tools are disabled by default and should only be enabled for non-production or least-privileged accounts.

## Pre-requisites

- Github Copilot and Copilot Chat extensions installed in VS Code
- Python 3.8 or later
- Azure CLI
- Access to the Fabric RTI database with appropriate permissions

## Installation

1. Clone the repository as you normally would:
2. Create a virtual environment and activate it:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```
3. Install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```
4. Create a `.env` file in the root of the project and set the necessary environment variables for the services you plan to enable:

    ```bash
    # Azure Kusto/Fabric Configuration
    CLUSTER_URL=<Your_Fabric_RTI_Cluster_URL>
    DATABASE_NAME=<Your_Fabric_RTI_Database_Name>

    # PostgreSQL Configuration
    POSTGRES_CONNECTION_STRING=postgresql://username:password@hostname:5432/database_name?sslmode=prefer
    
    # Service feature flags (set to "true" or "false")
    # All services are disabled by default for safety
    ENABLE_DATA_TOOLS=false
    ENABLE_FABRIC_RTI_TOOLS=false
    ENABLE_GIT_CLI_TOOLS=false
    ENABLE_INSTRUCTION_TOOLS=false
    ENABLE_POSTGRESQL_READ_TOOLS=false
    ENABLE_POSTGRESQL_WRITE_TOOLS=false
    ```
5. If you want PostgreSQL tools:

   - Enable `ENABLE_POSTGRESQL_READ_TOOLS=true` for read-only queries.
   - Enable `ENABLE_POSTGRESQL_WRITE_TOOLS=true` only when you explicitly want `INSERT`, `UPDATE`, or `DELETE` support.
    - Set `POSTGRES_CONNECTION_STRING` to a full PostgreSQL DSN, for example `postgresql://username:password@hostname:5432/database_name?sslmode=prefer`.
   - The write tool rejects DDL/admin statements such as `CREATE`, `ALTER`, `DROP`, and `TRUNCATE`, as well as multi-statement payloads.
   - Prefer a non-production database or a least-privileged account for write access.
6. Login to Azure using the Azure CLI and select the appropriate account and subscription if you plan to use Fabric RTI:

    ```bash
    az login
    ```
7. Add the MCP server in your `.vscode/mcp.json` file:

    ```json
    {
        "servers": {
            "friendly-mcp-tools": {
                "url": "http://127.0.0.1:8000/mcp",
                "type": "http"
            }
        },
        "inputs": []
    }
    ```
8. Start the server:
    ```bash
    python -m server
    ```
9. Start the server by clicking on "Start" just above the server configuration in your `.vscode/mcp.json` file.
10. Go to Github Copilot tools list and make sure "friendly-mcp-tools" server is available and selected.

## PostgreSQL tools

The PostgreSQL integration exposes two separate tools:

- A read tool for single-statement `SELECT` / `WITH` queries.
- A write tool for single-statement `INSERT`, `UPDATE`, and `DELETE` queries.

Safety constraints:

- Read and write tools are controlled by separate feature flags.
- Write access is disabled by default.
- The write tool is marked as destructive and rejects DDL/admin statements and multi-statement payloads.
- Use a non-production database or least-privileged PostgreSQL user for any write access.