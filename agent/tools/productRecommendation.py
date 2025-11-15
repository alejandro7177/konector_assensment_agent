import os, json, re
import openai
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from typing import Optional
from langchain_core.tools import BaseTool
from preprocessing.chroma import Chroma
from pydantic import BaseModel, Field

class RecommendationSchema(BaseModel):
    query: str = Field(..., description="User query to recommend electrical attenuators Series")

class ProductRecommendationTool(BaseTool):
    name:str = "ProductRecommendationTool"
    description: str = (
        "Use this tool to generate a recommendation of electrical attenuator series based on the user's product requirements."
        "The input should be a detailed description of the user's needs."
        "The output is a JSON file containing a list of recommended attenuators based on the input, with a specific ID, a description, and a set of metadata for each attenuator in the following format:{'id': 'xxxxxxxxx', 'page_content':'text', 'metadata':{}}"
    )
    args_schema: type[BaseModel] = RecommendationSchema 

    def _run(self, query: str) -> str:
        try:
            wheres = self.generate_filter(query)

            Store = Chroma(
                embeddings=OpenAIEmbeddings(
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    model="text-embedding-3-large"
                ),
                host=os.environ.get("CHROMA_DB_HOST"),
                port=os.environ.get("CHROMA_DB_PORT"),
                k=3
            )

            collection = Store.get_or_create_collection("test_collection")
            results = Store.query(collection, query, wheres)
            return json.dumps(results, indent=1)
        except Exception as ex:
            return f"Error during product recommendation: {ex}"

    def generate_filter(self, query: str) -> Optional[dict]:
        try:
            client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))
            
            prompt_system = ""
            with open("agent/prompts/generateFilterDB.md", "r", encoding="utf-8") as f:
                prompt_system = f.read()

            raw = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": query}
                ]
            )

            match = re.search(
                r"```json\s*(.*?)```", 
                raw.choices[0].message.content, 
                re.DOTALL
            )
            if match:
                json_text = match.group(1)
            else:
                json_text = raw
            response = json.loads(json_text)
            return response 
        except Exception as ex:
            print(f"Error during generate filter: {ex}")
            return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env")

    tool = ProductRecommendationTool()

    result = tool.run(
        "I want a robust actuator for hazardous environments with an Duty Cycle of less than 200"
    )

    print(result)
    