import chromadb
import os
import json
from uuid import uuid4
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.api.types import EmbeddingFunction
from typing import Optional, List, Dict, Any


class Chroma:
    client : Optional[ClientAPI]
    error_client : Optional[str]
    embeddings : OpenAIEmbeddings
    n_results : Optional[int] = 10

    def __init__(
            self,
            embeddings: OpenAIEmbeddings,
            port: int =8000, 
            host: str= "localhost",
            k: int =10
        )-> None:
        try:
            self.embeddings = embeddings
            self.client = chromadb.HttpClient(
                host=host,
                port=port
            )
            self.n_results = k
        except Exception as ex:
            self.client = None
            self.error_client = ex. __str__()   

    def check_health(self)-> bool:
        if self.client is None:
            print(f"###### Error Connection ChromaDb: {self.error_client}######")
            return False
        return True

    def get_or_create_collection(self, collection_name)->Optional[Collection]:
        if self.client:
            return self.client.get_or_create_collection(name=collection_name)
        print(self.error_client)
        return None

    def query(self, collection:Collection, query:str, wheres:Dict=None)-> Dict[str,Any]:
        try:
            documents = []
            if collection:
                embed_query = self.embeddings.embed_query(query)
                documents = collection.query(
                    query_embeddings=embed_query,
                    where=wheres,
                    n_results=self.n_results,
                    include=["documents", "metadatas"]
                )
            print(" Documents retrieved from ChromaDb: ", documents)
            if documents["ids"] != [[]]:
                return [
                    {
                        "id": id,
                        "page_content": doc,
                        "metadata": metadata
                    } 
                    for id, doc, metadata in zip(
                        documents["ids"][0], 
                        documents["documents"][0], 
                        documents["metadatas"][0])
                ]
            print(f"""
                Documentos no recuperados:
                    Arg 
                        - collection_name= {collection.name}
                        - wheres = {wheres}
            """)
            return []
        except Exception as ex:
            print(f"Error during query ChromaDb {ex}")
            return []

    def get_document(self, collection: Collection, doc_id: str)-> Optional[Dict[str,Any]]:
        try:
            result = collection.get(ids=[doc_id], include=["documents", "metadatas"])
            if result and len(result["documents"]) > 0:
                return {
                    "id": result["ids"][0],
                    "page_content": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            return {}
        except Exception as ex:
            print(f"Error during get document ChromaDb {ex}")
            return None
        
    def add_document(
            self, 
            document:Dict[str,Any], 
            collection:Collection
        )-> List[str]:
        try:

            id = document.get("id", str(uuid4()))
            doc = document.get("doc")
            metadata = document.get("metadata", {})

            collection.add(
                ids=[id], 
                documents=[doc], 
                embeddings=self.embeddings.embed_query(doc),
                metadatas=[metadata]
            )
            return id
        except Exception as ex:
            print(f"Error during add documents ChromaDb {ex}")
            return []

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env")
    langchain_embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", 
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    chroma = Chroma(
        port=os.environ.get("CHROMA_DB_PORT"),
        host=os.environ.get("CHROMA_DB_HOST"),
        embeddings=langchain_embeddings,
        k = 10
    )

    print(chroma.check_health())
    print("Creando coleccion test_collection")
    collection = chroma.get_or_create_collection("test_collection")

    query = "I want a robust actuator for hazardous environments with an Duty Cycle of less than 200"
    wheres =  {"$and": [
        {"Enclosure Type": "Explosionproof"},
        {"Duty Cycle": {"$lt": 200}}
    ]}
    results = chroma.query(collection, query, wheres)
    print("Results: ", json.dumps(results, indent=2))