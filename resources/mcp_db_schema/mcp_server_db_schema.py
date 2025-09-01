import json
import os
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz

# Initialize FastMCP server with configuration
mcp = FastMCP(
    "TimeService",  # Name of the MCP server
    instructions="You are a tublbug db schema assistant that can provide the db schema for Tumblbug Database",  # Instructions for the LLM on how to use this tool
    host="0.0.0.0",  # Host address (0.0.0.0 allows connections from any IP)
    port=8008,  # Port number for the server
)

@mcp.tool()
async def get_db_schema_info() -> str:
    """
    Get the db schema for Tumblbug Database.
    Returns the original json content without any summary or abbreviation.
    """
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to db_schema.json
        schema_path = os.path.join(current_dir, "data", "db_schema.json")
        
        # Read and parse the JSON file
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
            
        return json.dumps(schema_data, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        return "Error: db_schema.json file not found"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in db_schema.json"
    except Exception as e:
        return f"Error reading schema: {str(e)}"

if __name__ == "__main__":
    # Start the MCP server with stdio transport
    # stdio transport allows the server to communicate with clients
    # through standard input/output streams, making it suitable for
    # local development and testing
    mcp.run(transport="sse")
