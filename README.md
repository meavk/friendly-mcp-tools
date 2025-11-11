# Friendly MCP Tools

A collection of tools to interact with Microsoft Fabric RTI databases.

> Warning: Use an account with read-only access to the Fabric RTI database to avoid accidental data modifications.

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
4. Create a `.env` file in the root of the project and set the necessary environment variables for connecting to the Fabric RTI database:

    ```bash
    # Azure Kusto/Fabric Configuration
    CLUSTER_URL=<Your_Fabric_RTI_Cluster_URL>
    DATABASE_NAME=<Your_Fabric_RTI_Database_Name>
    ```
5. Login to Azure using the Azure CLI and select the appropriate account and subscription:

    ```bash
    az login
    ```
6. Add the MCP server in your `.vscode/mcp.json` file:

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
6. Start the server:
    ```bash
    python -m server
    ```
7. Start the server by clicking on "Start" just above the server configuration in your `.vscode/mcp.json` file.
8. Go to Github Copilot tools list and make sure "friendly-mcp-tools" server is available and selected.