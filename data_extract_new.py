from mcp.server.fastmcp import FastMCP

import pandas as pd
from typing import Any
import os, sys, glob

mcp = FastMCP(
    "Extract",
    instructions="Data Extract engine.",
)

# File reading tools
@mcp.tool()
def extract_file(path: str) -> str:
    """
    Read and return the contents of a text file.
    
    Args:
        path: Path to the file to read
        
    Returns:
        The file contents as text
    """
    try:
        df = pd.read_csv(path)
        return df.select_dtypes(include='number').to_json(orient='records')
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a text file.
    
    Args:
        path: Path where the file should be written
        content: Text content to write to the file
        
    Returns:
        Confirmation message
    """
    print(f"Attempting to write file: {file_path}", file=sys.stderr)
    try:
        # file_path = safe_path(path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"    

if __name__ == "__main__":
    mcp.run(transport="stdio")
