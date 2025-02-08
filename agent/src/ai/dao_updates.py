from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime
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
    """Model for treasury changes."""
    amount: str
    token_symbol: str
    direction: Literal['inflow', 'outflow']

class GovernanceChange(BaseModel):
    """Model for governance parameter changes."""
    type: str
    previous_value: Optional[str]
    new_value: Optional[str]

class SocialSentiment(BaseModel):
    """Model for social sentiment analysis."""
    score: float  # -1 to 1
    trending_keywords: List[str]
    total_mentions: int

class ImpactAnalysis(BaseModel):
    """Model for proposal impact analysis."""
    summary: str
    affected_areas: List[str]
    risk_level: Optional[Literal['low', 'medium', 'high']]

class UpdateAction(BaseModel):
    """Model for update actions."""
    type: Literal['link', 'vote', 'delegate']
    label: str
    url: str

class DaoUpdate(BaseModel):
    """Model for DAO updates."""
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
    """Agent for analyzing and generating DAO updates with AI-powered insights."""
    
    def __init__(self, tally_api_key: str, llm: Optional[BaseChatModel] = None):
        """Initialize the DAO Updates Agent."""
        logger.info("Initializing DAO Updates Agent")
        
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
        
        # Initialize Tally Client with API key
        logger.info("Initializing Tally Client")
        os.environ['TALLY_API_KEY'] = tally_api_key
        self.tally_client = TallyClient()
        
        logger.info("DAO Updates Agent initialized successfully")

    def _invoke_llm(self, context: str) -> str:
        """Helper function to invoke LLM safely."""
        try:
            response = self.llm.invoke([HumanMessage(content=context)])
            return response.content.strip() if response and hasattr(response, "content") else "Error: No response from AI"
        except Exception as e:
            logger.error(f"LLM invocation error: {str(e)}")
            return "Error: Failed to generate AI response"

    def _analyze_proposal_impact(self, proposal_data: Dict) -> ImpactAnalysis:
        """Use LLM to analyze proposal impact."""
        title = proposal_data.get('metadata', {}).get('title', '')
        description = proposal_data.get('metadata', {}).get('description', '')

        context = f"""Analyze this governance proposal and determine its impact:
Proposal Title: {title}
Description: {description}

Please provide:
1. A brief summary of potential impact
2. Key areas affected
3. Risk level (low/medium/high)
Format:
Summary: [your summary]
Areas: [comma-separated list of affected areas]
Risk: [low/medium/high]
"""
        response = self._invoke_llm(context)

        # Parse response safely
        lines = response.split("\n")
        try:
            summary = lines[0].replace('Summary:', '').strip()
            areas = [area.strip() for area in lines[1].replace('Areas:', '').strip().split(',')]
            risk = lines[2].replace('Risk:', '').strip().lower()
            return ImpactAnalysis(summary=summary, affected_areas=areas, risk_level=risk)
        except Exception:
            return ImpactAnalysis(summary="Error analyzing proposal", affected_areas=["Unknown"], risk_level="medium")

    def _analyze_governance_stats(self, stats: Dict) -> str:
        """Use LLM to analyze governance statistics."""
        context = f"""Analyze these DAO governance statistics:
Active Proposals: {stats['active_count']}
Passed Proposals: {stats['passed_count']}
Failed Proposals: {stats['failed_count']}
Pending Proposals: {stats['pending_count']}
Provide a short summary explaining what these numbers mean.
"""
        return self._invoke_llm(context)

    def _analyze_treasury_status(self, treasury_data: Dict) -> str:
        """Use LLM to analyze treasury status."""
        context = f"""Analyze this DAO's treasury status:
Treasury Size: {treasury_data.get('treasury_size', 'Unknown')}
Major Holdings: {treasury_data.get('major_holdings', [])}
Recent Transactions: {treasury_data.get('recent_transactions', [])}
Provide a summary explaining its significance.
"""
        return self._invoke_llm(context)

    def _analyze_proposal_outcome(self, proposal: Dict, status: str) -> str:
        """Use LLM to analyze proposal outcome."""
        context = f"""Analyze this proposal's outcome:
Title: {proposal['metadata']['title']}
Status: {status.upper()}
Votes For: {proposal.get('voteStats', {}).get('for', {}).get('votesCount', '0')}
Votes Against: {proposal.get('voteStats', {}).get('against', {}).get('votesCount', '0')}
Explain why the proposal {status} and its impact.
"""
        return self._invoke_llm(context)

    async def get_dao_updates(self, dao_slug: str, user_holdings: Optional[Dict] = None) -> List[DaoUpdate]:
        """Get AI-curated updates for a DAO."""
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
                        id=f"prop_{proposal['id']}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title=f"Proposal: {proposal['metadata']['title']}",
                        description=impact.summary,
                        priority='urgent' if impact.risk_level == 'high' else 'important',
                        category='proposal',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={'proposal_id': proposal['id'], 'impact_analysis': impact.dict()},
                        actions=[UpdateAction(type='link', label='View Proposal', url=f"https://www.tally.xyz/gov/{dao_slug}/proposal/{proposal['id']}")]
                    ))

            logger.info(f"Generated {len(updates)} updates for DAO: {dao_slug}")
            return sorted(updates, key=lambda x: {'urgent': 0, 'important': 1, 'fyi': 2}[x.priority], reverse=True)

        except Exception as e:
            logger.error(f"Error getting DAO updates: {str(e)}")
            return []
