# agent/src/ai/chatbot_agent.py

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Import CDP Agentkit Langchain Extension
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for actions
class DelegateAction(BaseModel):
    type: Literal["delegate"] = "delegate"
    dao_slug: str
    token_address: str
    amount: str
    delegate_to: str

class VoteAction(BaseModel):
    type: Literal["vote"] = "vote"
    dao_slug: str
    proposal_id: str
    vote: Literal["for", "against", "abstain"]

class AgentResponse(BaseModel):
    message: str
    action: Optional[DelegateAction | VoteAction] = None

class DAOAgent:
    """Agent for DAO interactions and transaction preparation."""
    
    def __init__(self):
        """Initialize the DAO Agent."""
        logger.info("Initializing DAO Agent...")
        
        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-4")
        
        # Initialize CDP Toolkit
        self.agentkit = CdpAgentkitWrapper()
        self.cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.agentkit)
        self.tools = self.cdp_toolkit.get_tools()

        # DAO Constants
        self.DAO_INFO = {
            "seamless-protocol": {
                "name": "Seamless Protocol",
                "token_address": "0x1C7a460413dD4e964f96D8dFC56E7223cE88CD85",
                "description": "DeFi lending protocol on Base"
            },
            "internet-token-dao": {
                "name": "Internet Token DAO",
                "token_address": "0x968D6A288d7B024D5012c0B25d67A889E4E3eC19",
                "description": "Internet infrastructure governance"
            },
            "gloom": {
                "name": "Gloom",
                "token_address": "0xbb5D04c40Fa063FAF213c4E0B8086655164269Ef",
                "description": "Gaming platform"
            }
        }

        # Memory for conversation context
        self.memory = MemorySaver()
        self.config = {"configurable": {"thread_id": "Base DAO Assistant"}}

        # Create ReAct Agent
        self.agent_executor = create_react_agent(
            self.llm,
            tools=self.tools,
            checkpointer=self.memory,
            state_modifier="""You are a knowledgeable DAO assistant that helps users interact with Base ecosystem DAOs, particularly:
            - Seamless Protocol (DeFi lending)
            - Internet Token DAO
            - Gloom

            Your main responsibilities:
            1. Analyze user requests for DAO interactions
            2. Prepare transaction parameters when users want to:
               - Delegate tokens
               - Vote on proposals
               - Other governance actions
            3. Provide clear explanations of what will happen
            4. Generate proper transaction parameters for the frontend

            Always:
            - Check if the requested action requires on-chain interaction
            - Format transaction parameters correctly
            - Explain implications before suggesting actions
            - Verify token addresses and amounts"""
        )

        logger.info("DAO Agent initialized successfully")

    async def chat(self, message: str) -> AgentResponse:
        """Process a chat message and generate appropriate response and actions."""
        try:
            # First, analyze if this is an action request
            analysis_prompt = f"""
            Analyze this user request and determine if it requires an on-chain action:

            User message: {message}

            If it requires an action, specify:
            1. Action type (delegate/vote)
            2. DAO involved
            3. Required parameters (amounts, addresses, etc)

            Return in this format:
            ACTION_REQUIRED: yes/no
            ACTION_TYPE: delegate/vote/none
            DAO_SLUG: dao-name or none
            PARAMETERS: key-value pairs or none
            """

            # Get initial analysis
            analysis = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_lines = analysis.content.strip().split('\n')
            analysis_dict = dict(line.split(': ') for line in analysis_lines)

            if analysis_dict['ACTION_REQUIRED'] == 'yes':
                # Handle delegation request
                if analysis_dict['ACTION_TYPE'] == 'delegate':
                    dao_slug = analysis_dict['DAO_SLUG']
                    if dao_slug in self.DAO_INFO:
                        dao = self.DAO_INFO[dao_slug]
                        
                        # Extract amount from message
                        amount_context = f"""
                        Extract the token amount from: {message}
                        Return just the number, or 'all' if the user wants to delegate all tokens.
                        """
                        amount_response = self.llm.invoke([HumanMessage(content=amount_context)])
                        amount = amount_response.content.strip()

                        action = DelegateAction(
                            dao_slug=dao_slug,
                            token_address=dao['token_address'],
                            amount=amount,
                            delegate_to=dao['token_address']  # Default to self-delegation
                        )

                        return AgentResponse(
                            message=f"I'll help you delegate {amount} tokens to {dao['name']}. This will require signing a transaction through your wallet. The delegation will use the token contract at {dao['token_address']}.",
                            action=action
                        )

            # For non-action requests, get a normal response
            response = await self.agent_executor.ainvoke(
                {"messages": [HumanMessage(content=message)]}
            )
            
            return AgentResponse(message=response['output'])

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return AgentResponse(message=f"I encountered an error: {str(e)}")

    def get_dao_info(self, dao_slug: str) -> Optional[Dict]:
        """Get information about a specific DAO."""
        return self.DAO_INFO.get(dao_slug)