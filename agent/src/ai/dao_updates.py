# agent/src/ai/dao_updates.py

from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import os
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
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
    def __init__(self, cdp_credentials: Dict[str, Any], llm: Optional[BaseChatModel] = None):
        """Initialize the DAO Updates Agent.
        
        Args:
            cdp_credentials: Credentials for CDP (should include cdp_api_key_name and cdp_api_key_private_key)
            llm: Optional pre-configured LLM for testing
        """
        # Initialize LLM
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
        
        # Transform credentials to CDP format
        cdp_formatted_creds = {
            'cdp_api_key_name': cdp_credentials.get('api_key_name'),
            'cdp_api_key_private_key': cdp_credentials.get('api_key_private_key')
        }


    def _analyze_proposal_impact(self, proposal_data: Dict) -> ImpactAnalysis:
        """Use LLM to analyze proposal impact."""
        try:
            context = f"""Analyze this governance proposal and determine its impact:

Proposal Title: {proposal_data.get('title')}
Description: {proposal_data.get('description')}

Please provide:
1. A brief summary of potential impact
2. Key areas affected
3. Risk level (low/medium/high) based on scope and complexity

Format your response exactly as follows:
Summary: [your summary]
Areas: [comma-separated list of affected areas]
Risk: [low/medium/high]
"""
            response = self.llm.invoke(input=HumanMessage(content=context))
            
            # Parse LLM response
            lines = response.content.strip().split('\n')
            summary = lines[0].replace('Summary:', '').strip()
            areas = [area.strip() for area in lines[1].replace('Areas:', '').strip().split(',')]
            risk = lines[2].replace('Risk:', '').strip().lower()
            
            return ImpactAnalysis(
                summary=summary,
                affected_areas=areas,
                risk_level=risk
            )
        except Exception as e:
            logger.error(f"Error analyzing proposal impact: {str(e)}")
            return ImpactAnalysis(
                summary="Could not analyze impact",
                affected_areas=["Unknown"],
                risk_level="medium"
            )

    def _analyze_treasury_change(self, treasury_data: Dict) -> Dict[str, Any]:
        """Analyze significance of treasury changes."""
        try:
            current_balance = float(treasury_data.get('balance', 0))
            previous_balance = float(treasury_data.get('previous_balance', 0))
            token_symbol = treasury_data.get('token_symbol', 'tokens')
            
            change = current_balance - previous_balance
            percent_change = (change / previous_balance * 100) if previous_balance > 0 else 0
            
            # Determine significance
            if abs(percent_change) > 20:
                priority = 'urgent'
            elif abs(percent_change) > 10:
                priority = 'important'
            else:
                priority = 'fyi'
                
            details = TreasuryChange(
                amount=str(abs(change)),
                token_symbol=token_symbol,
                direction='inflow' if change > 0 else 'outflow'
            )
            
            return {
                'summary': f"{'Increase' if change > 0 else 'Decrease'} of {abs(percent_change):.1f}% in treasury balance",
                'priority': priority,
                'details': details
            }
        except Exception as e:
            logger.error(f"Error analyzing treasury change: {str(e)}")
            return None

    def _get_social_sentiment(self, dao_slug: str, timeframe_hours: int = 24) -> SocialSentiment:
        """Analyze social sentiment from governance forums and discussions."""
        # Mock implementation - replace with actual sentiment analysis
        return SocialSentiment(
            score=0.5,
            trending_keywords=["governance", "proposal", "community"],
            total_mentions=100
        )

    async def get_dao_updates(self, dao_slug: str, user_holdings: Optional[Dict] = None) -> List[DaoUpdate]:
        """Get AI-curated updates for a DAO."""
        try:
            updates: List[DaoUpdate] = []
            
            # Fetch DAO data
            dao_data = self.tally_client.get_organization(dao_slug)
            if not dao_data or 'data' not in dao_data:
                logger.error(f"Failed to fetch data for DAO: {dao_slug}")
                return []

            org_data = dao_data['data']['organization']
            
            # Get active proposals
            proposals = self.tally_client.get_proposals(org_data['id'], include_active=True)
            
            # Process each proposal
            if proposals and 'data' in proposals and 'proposals' in proposals['data']:
                for proposal in proposals['data']['proposals']['nodes']:
                    impact = self._analyze_proposal_impact(proposal)
                    
                    # Determine priority based on impact
                    priority = 'urgent' if impact.risk_level == 'high' else \
                              'important' if impact.risk_level == 'medium' else 'fyi'

                    updates.append(DaoUpdate(
                        id=f"prop_{proposal['id']}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title=proposal['metadata']['title'],
                        description=impact.summary,
                        priority=priority,
                        category='proposal',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={
                            'proposal_id': proposal['id'],
                            'proposal_title': proposal['metadata']['title'],
                            'impact_analysis': impact.dict(),
                            'social_sentiment': self._get_social_sentiment(dao_slug).dict()
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

            return sorted(updates, key=lambda x: (
                {'urgent': 0, 'important': 1, 'fyi': 2}[x.priority],
                x.timestamp
            ), reverse=True)

        except Exception as e:
            logger.error(f"Error getting DAO updates: {str(e)}")
            return []