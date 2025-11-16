from langchain_core.tools import BaseTool
from preprocessing.chroma import Chroma
from pydantic import BaseModel, Field
from typing import Optional
import json


class SpecificDataRetrievalShema(BaseModel):
    id: str = Field(..., description="Unique identifier of the data to retrieve Base Part Number")

class SpecificDataRetrievalTool(BaseTool):
    name="SpecificDataRetrievalTool"
    description=(
        "Use this tool to retrieve specific data based on a unique identifier (Base Part Number)."
        "The input should be the unique identifier of the data to retrieve."
        "The output is a JSON file containing the data associated with the given identifier."
    )
    args_schema: type[BaseModel] = SpecificDataRetrievalShema

    def _run(self, id: str) -> str:
        try:
            Store = Chroma(
                embeddings=None,
                host="localhost",
                port=8000,
                k=1
            )

            collection = Store.get_or_create_collection("test_collection")
            wheres = {"Base Part Number": id}
            results = Store.get_documents(
                collection=collection,
                wheres=wheres,
                limit=1,
                doc_ids=None
            )
            return json.dumps(results["documents"], indent=1)
        except Exception as ex:
            return f"Error during specific data retrieval: {ex}"