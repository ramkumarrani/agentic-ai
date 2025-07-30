from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv
from typing import Any
import os

load_dotenv()

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("OPENAI_API_BASE")
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"] = os.getenv("OPENAI_DEPLOYMENT_NAME")

llm = AzureChatOpenAI(
    openai_api_version = os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_retriever(doc_file=None) -> Any:
    """
    create a rag solution
    """
    global doc_path
    if doc_file:
        doc_path = doc_file
    
    print(f"Loading document: {doc_path}")
    loader = PyMuPDFLoader(doc_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    split_documents = text_splitter.split_documents(docs)

    embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002-2-fas-dv")

    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

    retriever = vectorstore.as_retriever()
    return retriever

mcp = FastMCP(
    "Retriever",
    instructions="A Retriever that can retrieve information from the database.",
    port = 8003,
)

@mcp.tool()
async def retriever(query, doc_file=None) -> Any:
    """
    Retrieves information from the document database based on the query.
    Parameters:
        query (str): The query to search for in the document
        doc_file (str, optional): Path to the PDF document to use. If not provided, will use the default.
    """
    retriever = create_retriever(doc_file)
    prompt = hub.pull("rlm/rag-prompt")
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    retrieved_docs = rag_chain.invoke(query)
    return retrieved_docs

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
