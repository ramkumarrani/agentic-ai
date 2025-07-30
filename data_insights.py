from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv
from typing import Any
import os

load_dotenv()

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("OPENAI_API_BASE")
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"] = os.getenv("OPENAI_DEPLOYMENT_NAME")

model = AzureChatOpenAI(
    openai_api_version = os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

mcp = FastMCP(
    "insights",
    instructions="Data Insights engine.",
)

@mcp.tool()
async def insights(query: str) -> Any:
    """
    Insights from the data
    Parameters:
        query (str): The query 
    """
    prompt_template = ChatPromptTemplate([
    ("system", "You are a helpful AI assistant"),
    ("user", "Run data insights on: {topic} and provide a summary of the findings.")
    ])

    prompt = prompt_template.invoke({"topic": query})
    return model.invoke(prompt).content
    # return f"Going forward\nRam"

if __name__ == "__main__":
    mcp.run(transport="stdio")
