# agent/src/ai/chatbot_agent.py

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

# Import Tally Client - using relative import
from ..tally.client import TallyClient

# Load environment variables from project root
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class DAOGovernanceAgent:
    """Agent for analyzing and interacting with DAOs."""
    
    def __init__(self):
        """Initialize the DAO Governance Agent."""
        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-4-0125-preview")
        
        # Initialize CDP AgentKit
        self.cdp = CdpAgentkitWrapper()
        
        # Initialize CDP Toolkit
        self.cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.cdp)
        
        # Initialize Tally Client
        self.tally_client = TallyClient()
        
        # Create Agent
        self.agent_executor, self.config = self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the agent with CDP Agentkit tools and custom capabilities."""
        # Get CDP tools
        tools = self.cdp_toolkit.get_tools()
        
        # Store buffered conversation history in memory
        memory = MemorySaver()
        config = {"configurable": {"thread_id": "DAO Governance Assistant"}}

        # Create ReAct Agent
        agent = create_react_agent(
            self.llm,
            tools=tools,
            checkpointer=memory,
            state_modifier="""You are a knowledgeable DAO governance assistant that helps users understand and interact with DAOs. 
            You can analyze proposals, provide insights about treasury allocations, help with delegation decisions, and execute onchain actions.
            
            When analyzing proposals:
            1. Look at the proposal content, potential impacts, and historical context
            2. Consider both direct and indirect effects on the DAO
            3. Evaluate technical, financial, and governance implications
            
            When recommending delegates:
            1. Consider their voting history
            2. Look at their governance statements
            3. Evaluate their expertise and involvement
            
            For treasury-related questions:
            1. Provide clear breakdowns of allocations
            2. Consider historical treasury movements
            3. Explain the implications of changes
            
            Always:
            - Be clear about the implications of any onchain actions
            - Provide context and explanations for your recommendations
            - If asked to execute an action, first explain what will happen and ask for confirmation"""
        )
        
        return agent, config

    async def chat(self, message: str) -> str:
        """Process a chat message and return the response."""
        try:
            events = self.agent_executor.stream(
                {"messages": [HumanMessage(content=message)]},
                self.config,
                stream_mode="values"
            )
            
            responses = []
            for event in events:
                if "agent" in event:
                    responses.append(event["agent"]["messages"][0].content)
                elif "tools" in event:
                    responses.append(event["tools"]["messages"][0].content)
            
            return " ".join(responses)
            
        except Exception as e:
            return f"Error processing message: {str(e)}"

    def save_agent_state(self):
        """Export the agent's wallet data for persistence."""
        return self.cdp.export_wallet()

    def load_agent_state(self, wallet_data: str):
        """Load a previously saved agent state."""
        self.cdp = CdpAgentkitWrapper(cdp_wallet_data=wallet_data)
        self.cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.cdp)
        self.agent_executor, self.config = self._initialize_agent()