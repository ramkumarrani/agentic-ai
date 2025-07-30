from langgraph.prebuilt import create_react_agent
from langchain_openai import AzureChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
import streamlit as st

import asyncio, os
from dotenv import load_dotenv

load_dotenv()

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("OPENAI_API_BASE")
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"] = os.getenv("OPENAI_DEPLOYMENT_NAME")

model = AzureChatOpenAI(
    openai_api_version = os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

async def main(query_in: str):
    # Using absolute path to the server script
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server_rag.py")
    
    # Start the MCP client 
    client =  MultiServerMCPClient(
        {
            "rag": {
                "url": "http://localhost:8003/mcp/",
                "transport": "streamable_http",
            },
            "db": {
                "command": "python",
                "args": ["./db_server_new.py"],
                "transport": "stdio",
            },
            "math": {
                "command": "python",
                "args": ["./math_server.py"],
                "transport": "stdio",
            },
            "insights": {
                "command": "python",
                "args": ["./data_insights.py"],
                "transport": "stdio",
            },
            "extract": {
                "command": "python",
                "args": ["./data_extract_new.py"],
                "transport": "stdio",
            },
        }
    )
    
    try:
        # Get the tools from the server
        tools = await client.get_tools()
        
        # Get the PDF file path from the session state
        pdf_path = st.session_state.get("my_uploaded_file", "")
        await asyncio.sleep(2)
        print(f"File Path: {pdf_path}")
        
        # Create the agent
        agent = create_react_agent(model, tools)
        
        messages = [
            {"role": "system", "content": "You are an AI assistant that can perform multiple activites."},
            {"role": "user", "content": f"Use various tools provided to answer this question: {query_in}. Optionally, you may be provided with the document {pdf_path} to assist in answering this question."}
        ]
        
        # Invoke the agent
        result = await agent.ainvoke({"messages": messages})
        
        return result["messages"][-1].content
    finally:
        # Make sure to close the client connection
        # await client.aclose()
        pass


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    run_app=1

    # Apply custom CSS
    st.markdown("""
        <style>
        .big-title {
            font-size: 42px !important;
            font-weight: bold;
        }
        .medium-title {
            font-size: 32px !important;
        }
        .small-title {
            font-size: 20px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.sidebar.title("MCP Info")
    st.sidebar.text(f"\n\n\n\n\nFollowing MCP Servers\nare available for use:\n\n")
    # st.sidebar.markdown("<b>Remote Streamable HTTP Servers</b>", unsafe_allow_html=True )
    st.sidebar.markdown("<span style='font-weight:bold; color:red;'>Remote Streamable HTTP Servers</span>", unsafe_allow_html=True)
    # st.sidebar.text("Remote Streamable HTTP Servers")
    st.sidebar.text(f"1. RAG\n")
    st.sidebar.text(f"\n\n\n\n\n")
    st.sidebar.markdown("<span style='font-weight:bold; color:red;'>Local Servers</span>", unsafe_allow_html=True)
    # st.sidebar.text("Local Servers")
    st.sidebar.text(f"1. Database Access\n2. CSV Extraction\n3. Data Insights\n4. Simple Math\n")
    st.sidebar.text(f"\n\n\n\n\n")  
    
    st.set_page_config(page_title='🦜🔗 LLM Intelligence')
    st.title('🦜🔗 Agentic AI + MCP + RAG')
    st.markdown("<div class='small-title'>******************** An Autonomous, Reasoning LLM Engine *********************</div>", unsafe_allow_html=True)
    st.write(f"")

    uploaded_file = st.file_uploader(f'Upload a PDF/CSV', type = ["pdf", "csv"])
    query_text = st.text_area("Enter your query: ", value="", height=200, max_chars=1000)

    result = ''

    if st.button("submit query"):
        with st.spinner("Processing..."):
            if uploaded_file: # is None:
                # Save the uploaded file to disk
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state["my_uploaded_file"] = file_path
                # st.text(f'Successful: {file_path}')
            
            try:
                # We'll pass the query and file path to the main function
                response = asyncio.run(main(query_text))
                result = result + response
                st.text_area(
                        label="Output",
                        value=result,
                        height=300
                    )
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
                st.text(str(e))
