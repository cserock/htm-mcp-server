from typing import List, Optional, Any
import os

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS

from rag.base import RetrievalChain

class MDRetrievalChain(RetrievalChain):
    """
    MD-specific implementation of the RetrievalChain.
    
    This class specializes in loading, splitting, and indexing PDF documents
    for retrieval.
    """
    
    def __init__(self, 
                 source_uri: List[str], 
                 persist_directory: Optional[str] = None,
                 **kwargs) -> None:
        """
        Initialize a MD retrieval chain.
        
        Args:
            source_uri: List of MD file paths
            persist_directory: Directory to persist vector store
            **kwargs: Additional keyword arguments for the base RetrievalChain
        """

        super().__init__(source_uri=source_uri, persist_directory=persist_directory, **kwargs)
    
    def load_documents(self, source_uris: List[str]) -> List[Document]:
        """
        Load MD documents from file paths.
        
        Args:
            source_uris: List of MD file paths
            
        Returns:
            List of loaded documents
        """

        docs = []
        for source_uri in source_uris:
            if not os.path.exists(source_uri):
                print(f"File not found: {source_uri}")
                continue
                
            print(f"Loading MD: {source_uri}")
            loader = UnstructuredMarkdownLoader(source_uri, strategy="fast")
            docs.extend(loader.load())
        
        return docs
    
    def create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Create a text splitter optimized for PDF documents.
        
        Returns:
            A text splitter instance suitable for PDFs
        """
        
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50
        )
    
    def create_vectorstore(self, split_docs: List[Document]) -> Any:
        """
        Create a vector store from split MD documents.
        
        Args:
            split_docs: Split document chunks
            
        Returns:
            A vector store instance
            
        Raises:
            ValueError: If there are no split documents
        """
        
        FAISS_INDEX_NAME = "help_center"

        if not split_docs:
            raise ValueError("No split documents available.")
            
        if self.persist_directory:
            os.makedirs(self.persist_directory, exist_ok=True)
            
            if os.path.exists(self.persist_directory) and any(os.listdir(self.persist_directory)):
                print(f"Loading existing vector store: {self.persist_directory}")
                # 저장된 데이터를 로드
                # chroma 대신 faiss 사용
                # return FAISS(
                #     persist_directory=self.persist_directory,
                #     embedding_function=self.create_embedding()
                # )
                vectorstore = FAISS.load_local(
                    folder_path=self.persist_directory,
                    index_name=FAISS_INDEX_NAME,
                    embeddings=self.create_embedding(),
                    allow_dangerous_deserialization=True,
                )

                # 로드된 데이터를 확인
                print(vectorstore.index_to_docstore_id)

                return vectorstore
        
        print("Creating new vector store...")
        # chroma 대신 faiss 사용
        # vectorstore = Chroma.from_documents(
        #     documents=split_docs,
        #     embedding=self.create_embedding(),
        #     persist_directory=self.persist_directory
        # )
        vectorstore = FAISS.from_documents(
            documents=split_docs, 
            embedding=self.create_embedding()
        )

                # 로컬 Disk 에 저장
        vectorstore.save_local(folder_path=self.persist_directory, index_name=FAISS_INDEX_NAME)

        # 저장된 내용 확인
        print(vectorstore.docstore._dict)

        return vectorstore