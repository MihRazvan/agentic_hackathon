# agent/src/ai/dao_assistant.py

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import logging
from dotenv import load_dotenv

# Add project root to Python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
agent_dir = src_dir.parent
project_root = agent_dir.parent
sys.path.insert(0, str(project_root))

# Load environment variables from project root
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Verify required environment variables
required_vars = ['OPENAI_API_KEY', 'TALLY_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

from agent.src.tally.client import TallyClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DAOS = {
    "seamless-protocol": {
        "description": "DeFi lending protocol on Base",
        "token_id": "eip155:8453/erc20:0x1C7a460413dD4e964f96D8dFC56E7223cE88CD85"
    },
    "internet-token-dao": {
        "description": "Decentralized internet infrastructure governance",
        "token_id": "eip155:8453/erc20:0x968D6A288d7B024D5012c0B25d67A889E4E3eC19"
    },
    "gloom": {
        "description": "Decentralized gaming platform",
        "token_id": "eip155:8453/erc20:0xbb5D04c40Fa063FAF213c4E0B8086655164269Ef"
    }
}

class DAOAssistant:
    def __init__(self):
        logger.info("Initializing DAO Assistant...")
        
        # Initialize OpenAI with API key from environment
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        self.llm = ChatOpenAI(
            model="gpt-4-0125-preview", 
            temperature=0,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.tally_client = TallyClient()
        logger.info("DAO Assistant initialized successfully")

    async def get_proposal_analysis(self, dao_slug: str, proposal_id: str = None) -> str:
        """Analyze a specific proposal or latest proposal from a DAO."""
        try:
            # Get DAO data
            dao = self.tally_client.get_organization(dao_slug)
            
            # Get proposals
            proposals = self.tally_client.get_proposals(dao['data']['organization']['id'])
            
            if not proposals or 'data' not in proposals:
                return "Could not fetch proposal data."

            # Get specific or latest proposal
            target_proposal = None
            if proposal_id:
                for prop in proposals['data']['proposals']['nodes']:
                    if prop['id'] == proposal_id:
                        target_proposal = prop
                        break
            else:
                # Get latest proposal
                target_proposal = proposals['data']['proposals']['nodes'][0]

            if not target_proposal:
                return "Proposal not found."

            # Create context for LLM
            context = f"""
            Analyze this DAO proposal for {dao_slug}:
            
            Title: {target_proposal['metadata']['title']}
            Description: {target_proposal['metadata']['description']}
            Status: {target_proposal['status']}
            
            Provide:
            1. Summary of the proposal
            2. Main implications (technical, financial, governance)
            3. Potential risks and benefits
            4. Simple explanation (ELI5)
            """

            # Get LLM analysis
            response = self.llm.invoke([HumanMessage(content=context)])
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing proposal: {e}")
            return f"Error analyzing proposal: {str(e)}"

    async def get_delegate_recommendations(self, dao_slug: str) -> str:
        """Get delegate recommendations with analysis of their performance."""
        try:
            # Get DAO data
            dao = self.tally_client.get_organization(dao_slug)
            if not dao:
                return "Could not fetch DAO data."

            # Get delegates
            delegates_data = []
            delegates = self.tally_client.get_delegates(dao['data']['organization']['id'])
            
            if delegates and 'data' in delegates:
                for delegate in delegates['data']['delegates']['nodes']:
                    # Get delegate's voting history
                    votes = self.tally_client.get_votes_by_voter(
                        delegate['account']['address'], 
                        dao['data']['organization']['id']
                    )
                    
                    delegates_data.append({
                        'address': delegate['account']['address'],
                        'votes_count': delegate['votesCount'],
                        'delegators_count': delegate['delegatorsCount'],
                        'voting_history': votes
                    })

            # Create context for LLM
            context = f"""
            Analyze these delegates for {dao_slug}:
            
            Delegate Data: {delegates_data}
            
            Provide:
            1. Top 3 delegates based on:
               - Active participation
               - Voting power
               - Number of delegators
            2. Brief analysis of their voting patterns
            3. Recommendation for different voter profiles (active vs passive)
            """

            # Get LLM analysis
            response = self.llm.invoke([HumanMessage(content=context)])
            return response.content

        except Exception as e:
            logger.error(f"Error getting delegate recommendations: {e}")
            return f"Error getting delegate recommendations: {str(e)}"

    async def get_treasury_analysis(self, dao_slug: str) -> str:
        """Analyze DAO treasury allocation and movements."""
        try:
            # Get DAO data
            dao = self.tally_client.get_organization(dao_slug)
            if not dao:
                return "Could not fetch DAO data."

            org_data = dao['data']['organization']
            
            # Create context for LLM
            context = f"""
            Analyze the treasury data for {dao_slug}:
            
            Organization Data: {org_data}
            
            Provide:
            1. Current treasury breakdown
            2. Recent significant movements
            3. Key observations and recommendations
            4. Simple explanation of the treasury state
            """

            # Get LLM analysis
            response = self.llm.invoke([HumanMessage(content=context)])
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing treasury: {e}")
            return f"Error analyzing treasury: {str(e)}"

    async def chat(self, message: str) -> str:
        """Process a chat message about DAO governance."""
        try:
            # First, determine what the user is asking about
            intent_context = f"""
            Determine what the user is asking about from these categories:
            1. Proposal Analysis
            2. Delegate Recommendations
            3. Treasury Analysis
            4. Other/General Question

            User message: {message}
            
            Format: Return just the category number (1-4)
            """
            
            intent_response = self.llm.invoke([HumanMessage(content=intent_context)])
            intent = int(intent_response.content.strip())
            
            # Handle based on intent
            if intent == 1:
                # Extract DAO name from message
                for dao_slug in BASE_DAOS.keys():
                    if dao_slug in message.lower():
                        return await self.get_proposal_analysis(dao_slug)
            elif intent == 2:
                for dao_slug in BASE_DAOS.keys():
                    if dao_slug in message.lower():
                        return await self.get_delegate_recommendations(dao_slug)
            elif intent == 3:
                for dao_slug in BASE_DAOS.keys():
                    if dao_slug in message.lower():
                        return await self.get_treasury_analysis(dao_slug)
            
            # For general questions, provide context-aware response
            context = f"""
            You are a DAO governance assistant focused on these Base DAOs:
            {BASE_DAOS}
            
            User question: {message}
            
            Provide a helpful response focused on governance aspects and always mention if an action would require using the wallet for execution.
            """
            
            response = self.llm.invoke([HumanMessage(content=context)])
            return response.content

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Error processing message: {str(e)}"