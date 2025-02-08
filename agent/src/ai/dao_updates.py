# agent/src/ai/dao_updates.py

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
        """Initialize the DAO Updates Agent.
        
        Args:
            tally_api_key: The API key for Tally
            llm: Optional pre-configured LLM for testing
        """
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

    def _analyze_proposal_impact(self, proposal_data: Dict) -> ImpactAnalysis:
        """Use LLM to analyze proposal impact."""
        try:
            title = proposal_data.get('metadata', {}).get('title', '')
            description = proposal_data.get('metadata', {}).get('description', '')
            
            context = f"""Analyze this governance proposal and determine its impact:

Proposal Title: {title}
Description: {description}

Please provide:
1. A brief summary of potential impact
2. Key areas affected
3. Risk level (low/medium/high) based on scope and complexity

Format your response exactly as follows:
Summary: [your summary]
Areas: [comma-separated list of affected areas]
Risk: [low/medium/high]
"""
            logger.debug(f"Analyzing proposal impact for: {title}")
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

    def _analyze_governance_stats(self, stats: Dict) -> str:
        """Use LLM to analyze and explain governance statistics."""
        context = f"""Analyze these DAO governance statistics and provide a clear, simple explanation:

Active Proposals: {stats['active_count']}
Passed Proposals: {stats['passed_count']}
Failed Proposals: {stats['failed_count']}
Pending Proposals: {stats['pending_count']}

Please provide a brief, engaging summary that explains what these numbers mean for the DAO's health and activity.
Focus on making it easy to understand for someone new to DAOs.
"""
        response = self.llm.invoke(input=HumanMessage(content=context))
        return response.content

    def _analyze_treasury_status(self, treasury_data: Dict) -> str:
        """Use LLM to analyze and explain treasury status."""
        context = f"""Analyze this DAO's treasury information and explain its significance:

Treasury Size: {treasury_data.get('treasury_size', 'Unknown')}
Major Holdings: {treasury_data.get('major_holdings', [])}
Recent Transactions: {treasury_data.get('recent_transactions', [])}

Please provide:
1. A simple explanation of the treasury's current state
2. Any notable changes or patterns
3. What this means for the DAO's financial health

Make the explanation accessible to someone who isn't deeply familiar with crypto or DAOs.
"""
        response = self.llm.invoke(input=HumanMessage(content=context))
        return response.content

    def _analyze_proposal_outcome(self, proposal: Dict, status: str) -> str:
        """Use LLM to analyze and explain a proposal's outcome."""
        vote_stats = proposal.get('voteStats', [])
        vote_summary = {stat['type']: stat for stat in vote_stats}
        
        context = f"""Analyze this proposal's outcome and explain its significance:

Title: {proposal['metadata']['title']}
Status: {status.upper()}
Votes For: {vote_summary.get('for', {}).get('votesCount', '0')}
Votes Against: {vote_summary.get('against', {}).get('votesCount', '0')}
Description: {proposal['metadata'].get('description', 'No description available')}

Please explain:
1. What was this proposal trying to achieve?
2. Why did it {status}?
3. What does this mean for the DAO?

Make the explanation clear and accessible, avoiding technical jargon where possible.
"""
        response = self.llm.invoke(input=HumanMessage(content=context))
        return response.content

    def _generate_delegation_advice(self, user_holdings: str, dao_name: str) -> str:
        """Use LLM to generate personalized delegation advice."""
        context = f"""Generate personalized delegation advice for a user:

DAO Name: {dao_name}
User's Token Holdings: {user_holdings}

Please provide:
1. A brief explanation of why delegation is important
2. What their tokens could mean for the DAO's governance
3. A clear call to action

Make it personal and encouraging, helping them understand why their participation matters.
"""
        response = self.llm.invoke(input=HumanMessage(content=context))
        return response.content

    def _get_social_sentiment(self, dao_slug: str, timeframe_hours: int = 24) -> SocialSentiment:
        """Analyze social sentiment from governance forums and discussions."""
        try:
            logger.debug(f"Getting social sentiment for DAO: {dao_slug}")
            # TODO: Implement actual social sentiment analysis
            # For now, return realistic mock data
            return SocialSentiment(
                score=0.7,
                trending_keywords=["governance", "proposal", "community"],
                total_mentions=150
            )
        except Exception as e:
            logger.error(f"Error getting social sentiment: {str(e)}")
            return SocialSentiment(
                score=0.0,
                trending_keywords=[],
                total_mentions=0
            )

    async def get_dao_updates(self, dao_slug: str, user_holdings: Optional[Dict] = None) -> List[DaoUpdate]:
        """Get AI-curated updates for a DAO.
        
        Args:
            dao_slug: The DAO's slug/identifier
            user_holdings: Optional dictionary of user's token holdings
            
        Returns:
            List of DAO updates sorted by priority
        """
        try:
            logger.info(f"Getting updates for DAO: {dao_slug}")
            updates: List[DaoUpdate] = []
            
            # Fetch DAO data
            dao_data = self.tally_client.get_organization(dao_slug)
            if not dao_data or 'data' not in dao_data:
                logger.error(f"Failed to fetch data for DAO: {dao_slug}")
                return []

            org_data = dao_data['data']['organization']
            
            # Get all proposals
            proposals = self.tally_client.get_proposals(org_data['id'], include_active=False)
            
            if proposals and 'data' in proposals and 'proposals' in proposals['data']:
                proposal_nodes = proposals['data']['proposals']['nodes']
                
                # Group proposals by status
                active_proposals = [p for p in proposal_nodes if p['status'] == 'active']
                passed_proposals = [p for p in proposal_nodes if p['status'] == 'succeeded']
                failed_proposals = [p for p in proposal_nodes if p['status'] == 'defeated']
                pending_proposals = [p for p in proposal_nodes if p['status'] == 'pending']
                
                # Process active proposals
                for proposal in active_proposals:
                    impact = self._analyze_proposal_impact(proposal)
                    updates.append(DaoUpdate(
                        id=f"active_prop_{proposal['id']}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title=f"Active Proposal: {proposal['metadata']['title']}",
                        description=impact.summary,
                        priority='urgent' if impact.risk_level == 'high' else 'important',
                        category='proposal',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={
                            'proposal_id': proposal['id'],
                            'proposal_title': proposal['metadata']['title'],
                            'impact_analysis': impact.dict(),
                            'social_sentiment': self._get_social_sentiment(dao_slug).dict(),
                            'vote_stats': proposal.get('voteStats', []),
                            'ai_explanation': self._analyze_proposal_impact(proposal).summary
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
                
                # Add updates for recently passed proposals
                for proposal in passed_proposals[:2]:
                    explanation = self._analyze_proposal_outcome(proposal, 'passed')
                    updates.append(DaoUpdate(
                        id=f"passed_prop_{proposal['id']}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title=f"Proposal Passed: {proposal['metadata']['title']}",
                        description=explanation,
                        priority='important',
                        category='governance',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={
                            'proposal_id': proposal['id'],
                            'proposal_title': proposal['metadata']['title'],
                            'vote_stats': proposal.get('voteStats', []),
                            'execution_details': proposal.get('executableCalls', []),
                            'ai_explanation': explanation
                        }
                    ))
                
                # Add updates for recently failed proposals
                for proposal in failed_proposals[:2]:
                    explanation = self._analyze_proposal_outcome(proposal, 'failed')
                    updates.append(DaoUpdate(
                        id=f"failed_prop_{proposal['id']}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title=f"Proposal Defeated: {proposal['metadata']['title']}",
                        description=explanation,
                        priority='fyi',
                        category='governance',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={
                            'proposal_id': proposal['id'],
                            'proposal_title': proposal['metadata']['title'],
                            'vote_stats': proposal.get('voteStats', []),
                            'ai_explanation': explanation
                        }
                    ))
                
                # Add governance statistics update with AI analysis
                stats = {
                    'active_count': len(active_proposals),
                    'passed_count': len(passed_proposals),
                    'failed_count': len(failed_proposals),
                    'pending_count': len(pending_proposals)
                }
                stats_explanation = self._analyze_governance_stats(stats)
                updates.append(DaoUpdate(
                    id=f"gov_stats_{dao_slug}",
                    dao_slug=dao_slug,
                    dao_name=org_data['name'],
                    title="Governance Activity Overview",
                    description=stats_explanation,
                    priority='fyi',
                    category='governance',
                    timestamp=datetime.utcnow().isoformat(),
                    metadata={
                        'stats': stats,
                        'ai_explanation': stats_explanation
                    }
                ))
                
                # Add treasury snapshot with AI analysis
                if 'treasurySize' in org_data:
                    treasury_data = {
                        'treasury_size': org_data['treasurySize'],
                        'major_holdings': org_data.get('treasuryTokens', []),
                        'recent_transactions': org_data.get('recentTreasuryTx', [])
                    }
                    treasury_explanation = self._analyze_treasury_status(treasury_data)
                    updates.append(DaoUpdate(
                        id=f"treasury_{dao_slug}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title="Treasury Status",
                        description=treasury_explanation,
                        priority='important',
                        category='treasury',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={
                            **treasury_data,
                            'ai_explanation': treasury_explanation
                        }
                    ))
                
                # Add delegation advice if user has holdings
                if user_holdings and any(h for h in user_holdings.values() if float(h) > 0):
                    total_tokens = user_holdings.get(org_data.get('tokenId', ''), '0')
                    delegation_advice = self._generate_delegation_advice(total_tokens, org_data['name'])
                    updates.append(DaoUpdate(
                        id=f"delegation_{dao_slug}",
                        dao_slug=dao_slug,
                        dao_name=org_data['name'],
                        title="Your Delegation Opportunity",
                        description=delegation_advice,
                        priority='important',
                        category='governance',
                        timestamp=datetime.utcnow().isoformat(),
                        metadata={
                            'delegated_tokens': "0",
                            'total_tokens': total_tokens,
                            'ai_explanation': delegation_advice
                        },
                        actions=[
                            UpdateAction(
                                type='delegate',
                                label='Delegate Tokens',
                                url=f"https://www.tally.xyz/gov/{dao_slug}/delegate"
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