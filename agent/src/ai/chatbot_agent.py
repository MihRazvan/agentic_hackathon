# agent/src/ai/chatbot_agent.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure file to persist agent's CDP MPC Wallet Data
wallet_data_file = "wallet_data.txt"

def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    logger.info("Initializing DAO Agent...")
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4")
    
    # Load any existing wallet data
    wallet_data = None
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()
            logger.info("Loaded existing wallet data")

    # Configure CDP Agentkit Wrapper
    values = {}
    if wallet_data is not None:
        values = {"cdp_wallet_data": wallet_data}
    
    agentkit = CdpAgentkitWrapper(**values)
    
    # Persist the agent's CDP MPC Wallet Data
    wallet_data = agentkit.export_wallet()
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data)
        logger.info("Persisted wallet data")

    # Initialize CDP Toolkit and get tools
    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()
    logger.info(f"Loaded {len(tools)} CDP tools")

    # Store conversation history in memory
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "Base DAO Assistant"}}

    # Create ReAct Agent
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier="""You are a knowledgeable DAO assistant focused on Base ecosystem DAOs, particularly:
        - Seamless Protocol (DeFi lending)
        - Internet Token DAO (Decentralized internet infrastructure)
        - Gloom (Gaming platform)

        You can:
        1. Analyze proposals and their implications
        2. Help understand treasury allocations
        3. Guide users through delegation decisions
        4. Execute on-chain actions when required

        Network scope: All actions are on Base (base-sepolia for testing, base-mainnet for production)

        Always:
        - Be clear about implications of any on-chain actions
        - Explain what will happen before executing actions
        - If you need funds, request them from the faucet on base-sepolia
        - If asked to do something beyond your capabilities, explain what you can't do and suggest using CDP SDK
        
        For full documentation, refer users to docs.cdp.coinbase.com"""
    ), config

def run_chat_mode(agent_executor, config):
    """Run the agent in interactive chat mode."""
    print("Starting chat mode... Type 'exit' to end.")
    
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Run agent with user input
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)

def main():
    """Start the DAO agent."""
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    print("Starting DAO Agent...")
    agent_executor, config = initialize_agent()
    
    # Run in chat mode
    run_chat_mode(agent_executor=agent_executor, config=config)

if __name__ == "__main__":
    main()