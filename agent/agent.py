import json, os, uuid
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from agent.tools.productRecommendation import ProductRecommendationTool

class AgentActuator:
    def __init__(
        self, 
        tools: list,
        llm: BaseChatModel,
        system_prompt: str = ""
    ):
        self.tools = tools
        self.llm = llm
        self.system_prompt = system_prompt
        checkpointer = MemorySaver()
        self.agent = create_agent(
            name="agentActuator",
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            checkpointer=checkpointer
        )

    def invoke_agent(self, input, thread_id: str = str(uuid.uuid4())):
        return self.agent.invoke(
            input={"messages": [{"role": "user", "content": input}]}, 
            config={
                "configurable":{
                    "thread_id": thread_id
                }
            }
        )

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv(".env")
    thread = str(uuid.uuid4())

    llm = ChatOpenAI(
        temperature=0,
        model=os.environ.get("OPENAI_MODEL_NAME_CHAT", "gpt-4.1"),
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    tools = [ProductRecommendationTool()]
    system_prompt = """You are a technical expert specializing in 76 Series electric actuators. You must be able to communicate effectively with users to assist them with their technical needs. The following tools are available to you:
    ProductRecommendationTool: Use this tool to generate a recommendation of electrical attenuator series based on the user's product requirements. The input should be a detailed description of the user's needs. The output is a JSON file containing a list of recommended attenuators based on the input, with a specific ID, a description, and a set of metadata for each attenuator in the following format:{'id': 'xxxxxxxxx', 'page_content':'text', 'metadata':{}}
    """
    
    agent_actuator = AgentActuator(
        tools=tools,
        llm=llm,
        system_prompt=system_prompt
    )
    
    user_input = "Do you recommend two industrial-grade actuators with a torque of less than 100 Nm? What options do you have?"
    result =agent_actuator.invoke_agent(user_input, thread_id=thread)
    print("Agent Response: ", result)