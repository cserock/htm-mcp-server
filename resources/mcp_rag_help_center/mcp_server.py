import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from mcp.server.fastmcp import FastMCP

from rag import PDFRetrievalChain
from rag import MDRetrievalChain
import config
import subprocess
from zendesk_export.md import make_md_files

load_dotenv()

TBB_HELP_CENTER_MD_DATA_DIR = Path(os.getenv("TBB_HELP_CENTER_MD_DATA_DIR", config.TBB_HELP_CENTER_MD_DATA_DIR))

if TBB_HELP_CENTER_MD_DATA_DIR:
    os.makedirs(TBB_HELP_CENTER_MD_DATA_DIR, exist_ok=True)
    
    if not (os.path.exists(TBB_HELP_CENTER_MD_DATA_DIR) and any(os.listdir(TBB_HELP_CENTER_MD_DATA_DIR))):
        print("Creating new md files...")
        make_md_files()
    else:
        print(f"Loading existing md_files: {TBB_HELP_CENTER_MD_DATA_DIR}")

md_files = list(TBB_HELP_CENTER_MD_DATA_DIR.glob("*.md"))
md_paths = [str(path) for path in md_files]

VECTOR_DIR = Path(config.VECTOR_DIR)

rag_chain = MDRetrievalChain(
    source_uri = md_paths,
    persist_directory = str(VECTOR_DIR),
    k = config.DEFAULT_TOP_K,
    embedding_model = config.DEFAULT_EMBEDDING_MODEL,
    llm_model = config.DEFAULT_LLM_MODEL
).initialize()

# PDF
# DATA_DIR = Path(os.getenv("DATA_DIR", config.DATA_DIR))
# pdf_files = list(DATA_DIR.glob("*.pdf"))
# pdf_paths = [str(path) for path in pdf_files]

# VECTOR_DIR = Path(os.getenv("VECTOR_DIR", config.VECTOR_DIR))

# rag_chain = PDFRetrievalChain(
#     source_uri = pdf_paths,
#     persist_directory = str(VECTOR_DIR),
#     k = config.DEFAULT_TOP_K,
#     embedding_model = config.DEFAULT_EMBEDDING_MODEL,
#     llm_model = config.DEFAULT_LLM_MODEL
# ).initialize()

mcp = FastMCP(
    name="텀블벅 헬프센터 검색(RAG)",
    version="0.0.1",
    description="텀블벅 헬프센터 검색(RAG)",
    host="0.0.0.0",  # Host address (0.0.0.0 allows connections from any IP)
    port=8006, 
)

def format_search_results(docs: List[Document]) -> str:
    """
    Format search results as markdown.
    
    Args:
        docs: List of documents to format
        
    Returns:
        Markdown formatted search results

    """

    if not docs:
        return "No relevant information found."
    
    markdown_results = "## Search Results\n\n"
    
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown source")
        page = doc.metadata.get("page", None)
        page_info = f" (Page: {page+1})" if page is not None else ""
        
        markdown_results += f"### Result {i}{page_info}\n\n"
        markdown_results += f"{doc.page_content}\n\n"
        markdown_results += f"Source: {source}\n\n"
        markdown_results += "---\n\n"
    
    return markdown_results

# @mcp.tool()
# async def keyword_search(query: str, top_k: int = 3) -> str:
#     """
#     Performs keyword-based search on PDF documents.
#     Returns the most relevant results based on exact word/phrase matches.
#     Ideal for finding specific terms, definitions, or exact phrases in documents.
    
#     Parameters:
#         query: Search query
#         top_k: Number of results to return

#     """

#     try:
#         results = rag_chain.search_keyword(query, top_k)
#         return format_search_results(results)
#     except Exception as e:
#         return f"An error occurred during search: {str(e)}"

# @mcp.tool()
# async def semantic_search(query: str, top_k: int = 3) -> str:
#     """
#     Performs semantic search on PDF documents.
#     Finds content semantically similar to the query, delivering relevant information even without exact word matches.
#     Best for conceptual questions, understanding themes, or when you need information related to a topic.
    
#     Parameters:
#         query: Search query
#         top_k: Number of results to return

#     """

#     try:
#         results = rag_chain.search_semantic(query, top_k)
#         return format_search_results(results)
#     except Exception as e:
#         return f"An error occurred during search: {str(e)}"

@mcp.tool()
async def tbb_help_center_search(query: str, top_k: int = 3) -> str:
    """
    Performs hybrid search (keyword + semantic) on MD documents.
    Combines exact keyword matching and semantic similarity to deliver optimal results.
    The most versatile search option for general questions or when unsure which search type is best.
    
    Parameters:
        query: Search query
        top_k: Number of results to return

    """

    try:
        results = rag_chain.search_hybrid(query, top_k)
        print(results)
        return format_search_results(results)
    except Exception as e:
        return f"An error occurred during search: {str(e)}"

if __name__ == "__main__":
    mcp.run('sse')