import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from langgraph.prebuilt import create_react_agent
from agent.src.tally.client import TallyClient

# ✅ Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Load environment variables
load_dotenv()

class GovernanceChatbot:
    def __init__(self):
        """Initialize chatbot with AI model, CDP AgentKit, and Tally API Client."""
        logger.info("Initializing Governance Chatbot...")

        # ✅ Choose a cost-effective model
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")  # ✅ More efficient than GPT-4

        # ✅ Initialize CDP Wallet & AgentKit
        wallet_data_file = "wallet_data.txt"
        wallet_data = None

        if os.path.exists(wallet_data_file):
            with open(wallet_data_file) as f:
                wallet_data = f.read()

        values = {"cdp_wallet_data": wallet_data} if wallet_data else {}
        self.cdp = CdpAgentkitWrapper(**values)

        # ✅ Persist wallet data
        wallet_data = self.cdp.export_wallet()
        with open(wallet_data_file, "w") as f:
            f.write(wallet_data)

        # ✅ Initialize CDP Toolkit
        cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.cdp)
        tools = cdp_toolkit.get_tools()

        # ✅ Initialize Tally API Client
        self.tally_client = TallyClient()

        # ✅ Customize the AI state
        state_modifier = """
        You are an AI-powered Governance Assistant for DeFi protocols.
        You analyze governance proposals, predict outcomes, and help users delegate votes.
        You also retrieve treasury data and simulate governance decisions.
        Your responses should be **concise, accurate, and insightful**.
        """

        # ✅ Create AI Agent
        self.agent_executor = create_react_agent(self.llm, tools, state_modifier=state_modifier)

    def chat(self, user_input: str) -> str:
        """Processes user input and returns a response with retries and error handling."""
        
        # ✅ Handle DAO Queries using Tally API (with delay)
        if user_input.lower().startswith("dao "):
            dao_slug = user_input.split(" ", 1)[1]
            retries = 5
            delay = 2.0  # Start with a 2-second delay

            for attempt in range(retries):
                try:
                    dao_data = self.tally_client.get_organization(dao_slug)

                    if dao_data and "data" in dao_data and "organization" in dao_data["data"]:
                        dao = dao_data["data"]["organization"]
                        return f"\nDAO Name: {dao['name']}\nDescription: {dao['metadata']['description']}"
                    else:
                        return "DAO not found or invalid response from API."

                except Exception as e:
                    logger.error(f"Tally API Error: {str(e)}. Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff

            return "Error fetching DAO data. Please try again later."

        # ✅ Handle General AI Queries with Exponential Backoff
        retries = 5
        delay = 1.0  # Start with 1-second delay

        for attempt in range(retries):
            try:
                events = list(self.agent_executor.stream({"messages": [("user", user_input)]}))

                # ✅ Log the response structure for debugging
                logger.info(f"AI Response: {events}")

                if not events:
                    return "No response received from AI."

                # ✅ Extract messages safely
                messages = []
                for event in events:
                    if isinstance(event, dict):
                        # Extract AI response from 'agent' key
                        if "agent" in event and "messages" in event["agent"]:
                            for msg in event["agent"]["messages"]:
                                if hasattr(msg, "content"):
                                    messages.append(msg.content)

                        # Extract tool messages if available
                        elif "tools" in event and "messages" in event["tools"]:
                            for tool_msg in event["tools"]["messages"]:
                                if hasattr(tool_msg, "content"):
                                    messages.append(tool_msg.content)

                if messages:
                    return "\n".join(messages)
                else:
                    return "Response format unexpected. Check logs for details."

            except Exception as e:
                logger.error(f"Chatbot Error: {str(e)}. Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff

        return "There was an issue processing your request. Please try again later."


# ✅ Run chatbot interactively for testing
if __name__ == "__main__":
    bot = GovernanceChatbot()
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == "exit":
            break
        response = bot.chat(user_input)
        print(response)
