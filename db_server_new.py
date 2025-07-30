from mcp.server.fastmcp import FastMCP
import sqlite3
import json
from typing import Dict, List, Any

# create an MSP server
mcp = FastMCP("sqlite3 demo")

@mcp.tool()
def query_data(sql_query: str) -> str:
    conn = None
    cursor = None

    try:
        conn = sqlite3.connect("example.db")
        cursor = conn.cursor()
        # execute the sql query
        
        if sql_query.lower().startswith("select"):
            cursor.execute(sql_query)
            # fetch the results
            rows = cursor.fetchall()
        # elif sql_query.lower().startswith("insert"):
        elif (sql_query.lower().startswith("insert")) | (sql_query.lower().startswith("delete")):
            cursor.execute(sql_query)
            conn.commit()
            rows = 0
        else:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return json.dumps(rows, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")
