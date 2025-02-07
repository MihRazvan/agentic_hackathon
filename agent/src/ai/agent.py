from typing import Dict, Any, Optional
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from langchain_openai import ChatOpenAI
from ...src.tally.client import TallyClient  # Updated import path

class TabulaAgent:
    def __init__(self, cdp_credentials: Dict[str, Any]):
        # Initialize AI Model (GPT-4 or GPT-3.5-turbo)
        self.llm = ChatOpenAI(
            model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper responses
            temperature=0
        )
        
        # Initialize CDP AgentKit
        self.agentkit = CdpAgentkitWrapper(**cdp_credentials)
        self.toolkit = CdpToolkit.from_cdp_agentkit_wrapper(self.agentkit)
        
        # Initialize Tally Client
        self.tally_client = TallyClient()
        
    async def get_dao_summary(self, dao_slug: str) -> Dict[str, Any]:
        """Get a comprehensive DAO summary with AI-enhanced insights."""
        # Get raw data from Tally
        dao_data = self.tally_client.get_dao_metadata(dao_slug)
        proposals = self.tally_client.get_active_proposals(dao_data['data']['organization']['id'])
        
        # Use Claude to analyze and summarize
        context = f"""
        DAO Data: {dao_data}
        Active Proposals: {proposals}
        
        Please provide a concise summary of this DAO's current state, including:
        1. Key governance metrics
        2. Active proposal analysis
        3. Suggested actions for participants
        """
        
        response = await self.llm.apredict(context)
        return {
            "raw_data": {
                "dao": dao_data,
                "proposals": proposals
            },
            "ai_summary": response
        }