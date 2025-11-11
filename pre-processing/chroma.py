import chromadb
import os
from langchain_core.documents import Document
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.api.types import EmbeddingFunction
from typing import Optional, List


class Chroma:
    client : Optional[ClientAPI]
    error_client : Optional[str]
    embeddings : EmbeddingFunction
    n_results : Optional[int] = 10

    def __init__(self, port, host, embeddings):
        try:
            self.embeddings = embeddings
            self.client = chromadb.HttpClient(
                host=os.environ.get("CHROMA_DB_HOST"),
                port=os.environ.get("CHROMA_DB_PORT")
            )
        except Exception as ex:
            self.client = None
            self.error_client = ex.__str__

    def check_health(self)-> bool:
        if self.client is None:
            print(f"###### Error Connection ChromaDb: {self.error_client}######")
            return False
        return True

    def get_or_create_collection(self, collection_name)->Collection:
        return self.client.get_or_create_collection(name=collection_name)

    def query(self, collection_name, query, wheres):
        try:
            documents = []
            collection = self.get_or_create_collection(collection_name=collection_name)
            if collection:
                embed_query = self.embeddings.embed_query(query)
                documents = collection.query(
                    query_embeddings=embed_query,
                    where=wheres,
                    n_results=self.n_results
                )
            if documents:
                return documents
            print(f"""
                Documentos no recuperados:
                    Arg 
                        - collection_name= {collection_name}
                        - wheres = {wheres}
            """)
        except Exception as ex:
            print(f"Error during query ChromaDb {ex}")
            return []
    def add_documents(self, documents:List[str], collection:Collection):
        try:
            collection.add()
        except Exception as ex:
            print(ex)

    