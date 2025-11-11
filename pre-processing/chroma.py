import chromadb
import os
import json
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv(".env")
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

    def __init__(self, port, host, embeddings):
        try:
            self.embeddings = embeddings
            self.client = chromadb.HttpClient(
                host=os.environ.get("CHROMA_DB_HOST"),
                port=os.environ.get("CHROMA_DB_PORT")
            )
        except Exception as ex:
            self.client = None
            self.error_client = ex. __str__()

    def check_health(self)-> bool:
        if self.client is None:
            print(f"###### Error Connection ChromaDb: {self.error_client}######")
            return False
        return True

    def get_or_create_collection(self, collection_name)->Collection:
        return self.client.get_or_create_collection(name=collection_name)

    def query(self, collection_name, query, wheres= None)-> Dict[str,Any]:
        try:
            documents = []
            collection = self.get_or_create_collection(collection_name=collection_name)
            if collection:
                embed_query = self.embeddings.embed_query(query)
                documents = collection.query(
                    query_embeddings=embed_query,
                    where=wheres,
                    n_results=self.n_results,
                    include=["documents", "metadatas"]
                )
            if documents["ids"] != [[]]:
                print(documents)
                return [
                    {
                        "id": id,
                        "page_content": doc,
                        "metadata": metadata
                    } 
                    for id, doc, metadata in zip(
                        documents["ids"], 
                        documents["documents"], 
                        documents["metadatas"])
                ]
            print(f"""
                Documentos no recuperados:
                    Arg 
                        - collection_name= {collection_name}
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
        
    def add_documents(
            self, 
            documents:List[Dict[str,Any]], 
            collection:Collection
        )-> List[str]:
        try:
            ids = [str(uuid4()) for _ in documents]
            docs = [doc["doc"] for doc in documents]
            collection.add(
                ids=ids, 
                documents=docs, 
                embeddings=self.embeddings.embed_documents(docs),
                metadatas=[doc.get("metadata", {}) for doc in documents]
            )
            return ids
        except Exception as ex:
            print(f"Error during add documents ChromaDb {ex}")
            return []

if __name__ == "__main__":
    langchain_embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", 
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    chroma = Chroma(
        port=os.environ.get("CHROMA_DB_PORT"),
        host=os.environ.get("CHROMA_DB_HOST"),
        embeddings=langchain_embeddings
    )

    print(chroma.check_health())
    print("Creando coleccion test_collection")
    collection = chroma.get_or_create_collection("test_collection")
    # print("Coleccion creada")
    # print("Subiendo documentos test_docs")
    # docs = [
    #     {"doc": "Este es un documento de prueba", "metadata": {"source": "test2"}}, 
    #     {"doc": "Este es otro documento de prueba", "metadata": {"source": "test3"}}
    # ]

    # chroma.add_documents(docs, collection)
    # print("Documentos subidos")
    results =chroma.query("test_collection", "prueba", wheres={"source": "test3 "})
    print("Resultados de la consulta:")
    print(results)

    # doc = chroma.get_document(collection, "407f63ca-09ea-47b2-8913-4b5fc729cd4d")
    # print("Documento recuperado:")
    # print(json.dumps(doc, indent=2))