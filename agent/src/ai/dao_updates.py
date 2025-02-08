from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from ..tally.client import TallyClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TreasuryChange(BaseModel):
    amount: str
    token_symbol: str
    direction: Literal['inflow', 'outflow']

class GovernanceChange(BaseModel):
    type: str
    previous_value: Optional[str]
    new_value: Optional[str]

class SocialSentiment(BaseModel):
    score: float  # -1 to 1
    trending_keywords: List[str]
    total_mentions: int

class ImpactAnalysis(BaseModel):
    summary: str
    affected_areas: List[str]
    risk_level: Optional[Literal['low', 'medium', 'high']]

class UpdateAction(BaseModel):
    type: Literal['link', 'vote', 'delegate']
    label: str
    url: str

class DaoUpdate(BaseModel):
    id: str
    dao_slug: str
    dao_name: str
    title: str
    description: str
    priority: Literal['urgent', 'important', 'fyi']
    category: Literal['proposal', 'treasury', 'governance', 'social']
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    actions: Optional[List[UpdateAction]] = Field(default_factory=list)

class DaoUpdatesAgent:
    def __init__(self, tally_api_key: str, llm: Optional[BaseChatModel] = None):
        logger.info("Initializing DAO Updates Agent")
        
        if llm is not None:
            self.llm = llm
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
                
            self.llm = ChatOpenAI(
                api_key=api_key,
                model="gpt-4",
                temperature=0
            )
        
        logger.info("Initializing Tally Client")
        os.environ['TALLY_API_KEY'] = tally_api_key
        self.tally_client = TallyClient()
        
        logger.info("DAO Updates Agent initialized successfully")
    
    def _format_large_number(self, num):
        """Format large numbers for better readability."""
        try:
            num = int(num)
            if num >= 1_000_000_000:
                return f"{num / 1_000_000_000:.2f}B"
            elif num >= 1_000_000:
                return f"{num / 1_000_000:.2f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.2f}K"
            return str(num)
        except ValueError:
            return str(num)
    
    async def get_dao_updates(self, dao_slug: str, user_holdings: Optional[Dict] = None) -> List[DaoUpdate]:
        try:
            logger.info(f"Getting updates for DAO: {dao_slug}")
            updates: List[DaoUpdate] = []
            
            dao_data = self.tally_client.get_organization(dao_slug)
            if not dao_data or 'data' not in dao_data:
                logger.error(f"Failed to fetch data for DAO: {dao_slug}")
                return []
            
            org_data = dao_data['data']['organization']
            proposals = self.tally_client.get_proposals(org_data['id'], include_active=False)
            
            if proposals and 'data' in proposals and 'proposals' in proposals['data']:
                for proposal in proposals['data']['proposals']['nodes']:
                    impact = self._analyze_proposal_impact(proposal)
                    
                    updates.append(DaoUpdate(
                        id=f"proposal_{proposal['id']}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title=f"Proposal: {proposal['metadata']['title']}",
                        description=impact.summary,
                        priority='urgent' if impact.risk_level == 'high' else 'important',
                        category='proposal',
                        timestamp=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
                        metadata={
                            'proposal_id': proposal['id'],
                            'impact_analysis': impact.dict(),
                            'vote_stats': [
                                {
                                    "type": stat["type"],
                                    "votesCount": self._format_large_number(stat["votesCount"]),
                                }
                                for stat in proposal.get("voteStats", [])
                            ]
                        },
                        actions=[
                            UpdateAction(
                                type='link',
                                label='View Proposal',
                                url=f"https://www.tally.xyz/gov/{dao_slug}/proposal/{proposal['id']}"
                            ),
                            UpdateAction(
                                type='vote',
                                label='Vote Now',
                                url=f"https://www.tally.xyz/gov/{dao_slug}/proposal/{proposal['id']}/vote"
                            )
                        ]
                    ))
            
            logger.info(f"Generated {len(updates)} updates for DAO: {dao_slug}")
            return sorted(updates, key=lambda x: (
                {'urgent': 0, 'important': 1, 'fyi': 2}[x.priority],
                x.timestamp
            ), reverse=True)
        
        except Exception as e:
            logger.error(f"Error getting DAO updates: {str(e)}")
            return []
