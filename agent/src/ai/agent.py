# agent/src/ai/agent.py
from typing import Dict, Any, Optional
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from langchain_openai import ChatOpenAI
from agent.src.tally.client import TallyClient
from langchain_core.messages import HumanMessage

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
        
    def _process_dao_data(self, dao_data: Dict) -> Dict:
        """Extract relevant information from DAO data."""
        org = dao_data.get('data', {}).get('organization', {})
        return {
            'name': org.get('name'),
            'proposalsCount': org.get('proposalsCount'),
            'delegatesCount': org.get('delegatesCount'),
            'tokenOwnersCount': org.get('tokenOwnersCount'),
            'hasActiveProposals': org.get('hasActiveProposals')
        }

    def _process_proposals(self, proposals_data: Dict) -> list:
        """Extract relevant information from proposals."""
        proposals = proposals_data.get('data', {}).get('proposals', {}).get('nodes', [])
        return [{
            'title': p.get('metadata', {}).get('title'),
            'status': p.get('status'),
            'voteStats': p.get('voteStats', [])
        } for p in proposals[:5]]  # Limit to 5 most recent proposals
        
    async def get_dao_summary(self, dao_slug: str) -> Dict[str, Any]:
        """Get a comprehensive DAO summary with AI-enhanced insights."""
        try:
            # Get raw data from Tally
            dao_data = self.tally_client.get_dao_metadata(dao_slug)
            if not dao_data or 'data' not in dao_data:
                raise ValueError(f"Could not fetch data for DAO: {dao_slug}")
                
            org_id = dao_data['data']['organization']['id']
            proposals = self.tally_client.get_active_proposals(org_id)
            
            # Process data to reduce token count
            processed_dao = self._process_dao_data(dao_data)
            processed_proposals = self._process_proposals(proposals)
            
            # Create context for LLM
            context = f"""Analyze this DAO's current state and provide a concise summary:

DAO Information:
{processed_dao}

Active Proposals:
{processed_proposals}

Please provide:
1. Key governance metrics
2. Active proposal analysis
3. Suggested actions for participants

Keep the response structured and concise."""
            
            # Use LLM to analyze
            response = await self.llm.ainvoke(
                input=HumanMessage(content=context)
            )
            
            return {
                "raw_data": {
                    "dao": processed_dao,
                    "proposals": processed_proposals
                },
                "ai_summary": response.content
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "raw_data": None,
                "ai_summary": None
            }