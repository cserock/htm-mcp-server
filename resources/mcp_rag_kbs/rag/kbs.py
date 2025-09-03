from typing import List, Optional, Any
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from rag.base import PersistRetrievalChain

class KBSRetrievalChain(PersistRetrievalChain):
    """
    KBS-specific implementation of the PersistRetrievalChain.
    
    This class specializes in loading DB from Persist directory
    for retrieval.
    """
    
    def __init__(self, 
                 persist_directory: Optional[str] = None,
                 db_index_name: Optional[str] = None,
                 split_docs: Optional[List[Document]] = None,
                 **kwargs) -> None:
        """
        Initialize a KBS retrieval chain.
        
        Args:
            persist_directory: Directory to persist vector store
            db_index_name: Index name of the vector store
            **kwargs: Additional keyword arguments for the base RetrievalChain
        """

        super().__init__(persist_directory=persist_directory, db_index_name=db_index_name, split_docs=split_docs, **kwargs)
    
    def create_vectorstore(self) -> Any:
        """
        Create a vector store from split KBS documents.
        
        Args: 
            None
            
        Returns:
            A vector store instance
            
        Raises:
            ValueError: If there are no split documents
        """
        
        if not self.persist_directory:
            raise ValueError("No persist directory available.")

        vectorstore = None   
        if self.persist_directory:
            if os.path.exists(self.persist_directory) and any(os.listdir(self.persist_directory)):
                print(f"Loading existing vector store: {self.persist_directory}")

                # 저장된 데이터를 로드
                vectorstore = FAISS.load_local(
                    folder_path=self.persist_directory,
                    index_name=self.db_index_name,
                    embeddings=self.create_query_embedding(),
                    allow_dangerous_deserialization=True,
                )
        return vectorstore