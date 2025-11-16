from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from preprocessing.chroma import Chroma
from agent.tools.productRecommendation import ProductRecommendationTool
from agent.tools.specificDataRetrieval import SpecificDataRetrievalTool
from agent.agent import AgentActuator

@asynccontextmanager
async def lifespan(app: FastAPI):
    with open("agent/prompts/agent.md", "r", encoding="utf-8") as f:
        conversation_system_prompt = f.read()

    tools = [ProductRecommendationTool()]
    llm = ChatOpenAI(name="gpt-4.1", temperature=0)

    app.state.agent = AgentActuator(
        tools=tools,
        llm=llm,
        system_prompt=conversation_system_prompt,
    )

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Konector Assessment Agent API is running."}

@app.post("/api/conversation/")
async def conversation_endpoint(request: Request):
    try:
        request_data = await request.json()
        input_user = request_data.get("query", "")
        id_user = request_data.get("user_id", "default_user")
        result_agent = \
            request.app.state.agent.invoke_agent(
                input_user, id_user
            )

        return {"response": result_agent}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv(".env")
    uvicorn.run("api.api:app", host="0.0.0.0", port=8001, reload=True)