import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from mcp.server.fastmcp import FastMCP
from rag import KBSRetrievalChain
import config
import glob
import pickle
from langchain_teddynote import logging

load_dotenv()
DB_DIR = Path(config.DB_DIR)
PARSING_OUTPUT_DIR = Path(config.PARSING_OUTPUT_KBS_DIR)

logging.langsmith(project_name="htm-mcp-server")

def load_documents_from_pkl(filepath):
    """
    Pickle 파일에서 Langchain Document 리스트를 불러오는 함수

    Args:
        filepath: 원본 파일 경로 (예: path/to/filename.pdf)
    Returns:
        Langchain Document 객체 리스트
    """
    # 확장자 제거하고 절대 경로로 변환
    abs_path = os.path.abspath(filepath)
    base_path = os.path.splitext(abs_path)[0]
    pkl_path = f"{base_path}.pkl"

    with open(pkl_path, "rb") as f:
        documents = pickle.load(f)
    return documents

# load documentts from parsing_outputs
pkl_files = glob.glob(str(PARSING_OUTPUT_DIR / "*.pkl"))

if not pkl_files:
    print("❌ PARSING_OUTPUT_DIR에서 .pkl 파일을 찾을 수 없습니다.")
else:
    # 모든 .pkl 파일에서 문서 로드
    all_documents = []
    for pkl_file in pkl_files:
        print(f"📄 {pkl_file} 파일 로드 중...")  # 한국어 코멘트
        documents = load_documents_from_pkl(pkl_file)
        all_documents.extend(documents)

    print(f"✅ 총 {len(all_documents)}개의 문서가 로드되었습니다.")

rag_chain = KBSRetrievalChain(
    persist_directory = str(DB_DIR),
    db_index_name = config.DB_INDEX_NAME,
    k = config.DEFAULT_TOP_K,
    split_docs = all_documents,
).initialize()

mcp = FastMCP(
    name="킹덤빌더스쿨(KBS) 검색(RAG)",
    version="0.0.1",
    description="킹덤빌더스쿨(KBS) 검색(RAG)",
    host="0.0.0.0",  # Host address (0.0.0.0 allows connections from any IP)
    port=8001 
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

def format_search_results_with_image_metadata(docs: List[Document]) -> str:
    """
    이미지 메타데이터를 활용한 검색 결과 포맷팅
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
        
        # 이미지 정보가 있는 경우 추가
        if "images" in doc.metadata:
            images = doc.metadata["images"]
            if images:
                markdown_results += "**Related Images:**\n"
                for img in images:
                    markdown_results += f"- {img}\n"
                markdown_results += "\n"
        
        markdown_results += f"Source: {source}\n\n"
        markdown_results += "---\n\n"

        print(markdown_results)
    
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
async def search(query: str, top_k: int = 4) -> str:
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
        # print(results)
        return format_search_results_with_image_metadata(results)
    except Exception as e:
        return f"An error occurred during search: {str(e)}"

if __name__ == "__main__":
    mcp.run('sse')