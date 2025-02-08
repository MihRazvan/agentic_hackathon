# agent/src/api/delegation_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import logging
import os
from ..tally.client import TallyClient
from ..ai.dao_updates import DaoUpdatesAgent, DaoUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory (where .env is located)
root_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = root_dir / '.env'

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)
logger.info(f"Loading environment variables from: {env_path}")

# Log environment variable status (without exposing values)
for var in ['TALLY_API_KEY', 'OPENAI_API_KEY']:
    logger.info(f"{var} is {'set' if os.getenv(var) else 'not set'}")

app = FastAPI(title="Tabula API", description="DAO Intelligence Hub API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenHolding(BaseModel):
    token_address: str
    chain_id: str
    balance: str

class DelegationRequest(BaseModel):
    token_holdings: List[TokenHolding]

class UpdatesRequest(BaseModel):
    dao_slugs: List[str]
    token_holdings: Optional[Dict[str, str]] = None

def get_tally_client() -> TallyClient:
    """Get or create TallyClient instance."""
    tally_api_key = os.getenv('TALLY_API_KEY')
    if not tally_api_key:
        raise HTTPException(
            status_code=500,
            detail="TALLY_API_KEY environment variable is not set"
        )
    
    try:
        return TallyClient()
    except Exception as e:
        logger.error(f"Error initializing TallyClient: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize TallyClient"
        )

def get_updates_agent() -> DaoUpdatesAgent:
    """Get DaoUpdatesAgent instance."""
    tally_api_key = os.getenv('TALLY_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not tally_api_key:
        raise HTTPException(
            status_code=500,
            detail="TALLY_API_KEY environment variable is not set"
        )
        
    if not openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY environment variable is not set"
        )
    
    try:
        return DaoUpdatesAgent(tally_api_key=tally_api_key)
    except Exception as e:
        logger.error(f"Error initializing DaoUpdatesAgent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize DaoUpdatesAgent"
        )

@app.post("/api/delegations/{address}")
async def get_delegations(address: str, request: DelegationRequest):
    """Get delegations for a wallet address based on token holdings."""
    logger.info(f"Processing delegations for address: {address}")
    logger.info(f"Token holdings: {request.token_holdings}")
    
    try:
        # Get TallyClient instance
        tally_client = get_tally_client()
        
        # Get all Base DAOs
        orgs = tally_client.get_organizations()
        
        if not orgs or 'data' not in orgs or 'organizations' not in orgs['data']:
            raise HTTPException(status_code=500, detail="Failed to fetch organizations")
        
        base_daos = []
        for dao in orgs['data']['organizations']['nodes']:
            # Only include Base DAOs
            if 'eip155:8453' in dao.get('chainIds', []):
                base_daos.append(dao)
        
        logger.info(f"Found {len(base_daos)} Base DAOs")
        
        # Get active delegations
        active_delegations = []
        for dao in base_daos:
            delegate_info = tally_client.get_delegate_info(address, dao['id'])
            if delegate_info and delegate_info.get('delegatorCount', 0) > 0:
                active_delegations.append({
                    "dao_name": dao['name'],
                    "dao_slug": dao['slug'],
                    "token_amount": f"{delegate_info.get('votesCount', 0)} votes",
                    "chain_ids": dao['chainIds'],
                    "proposals_count": dao.get('proposalsCount', 0),
                    "has_active_proposals": dao.get('hasActiveProposals', False)
                })
        
        # Get available delegations (based on token holdings)
        available_delegations = []
        for dao in base_daos:
            # Skip if already delegating
            if any(d['dao_slug'] == dao['slug'] for d in active_delegations):
                continue
                
            # Check if user holds the governance token
            token_id = dao.get('tokenIds', [None])[0]
            if token_id:
                for holding in request.token_holdings:
                    if holding.token_address.lower() in token_id.lower():
                        available_delegations.append({
                            "dao_name": dao['name'],
                            "dao_slug": dao['slug'],
                            "token_amount": f"Balance: {holding.balance}",
                            "chain_ids": dao['chainIds'],
                            "proposals_count": dao.get('proposalsCount', 0),
                            "has_active_proposals": dao.get('hasActiveProposals', False)
                        })
        
        # Get recommended DAOs (most active ones)
        recommended_daos = sorted(
            [dao for dao in base_daos if dao['slug'] not in [d['dao_slug'] for d in active_delegations + available_delegations]],
            key=lambda x: (x.get('proposalsCount', 0), x.get('delegatesCount', 0)),
            reverse=True
        )[:3]
        
        recommended_delegations = [
            {
                "dao_name": dao['name'],
                "dao_slug": dao['slug'],
                "token_amount": f"{dao.get('delegatesCount', 0)} delegates",
                "chain_ids": dao['chainIds'],
                "proposals_count": dao.get('proposalsCount', 0),
                "has_active_proposals": dao.get('hasActiveProposals', False)
            }
            for dao in recommended_daos
        ]
        
        return {
            "active_delegations": active_delegations,
            "available_delegations": available_delegations,
            "recommended_delegations": recommended_delegations
        }
        
    except Exception as e:
        logger.error(f"Error processing delegations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/updates", response_model=List[DaoUpdate])
async def get_dao_updates(request: UpdatesRequest):
    """Get AI-curated updates for specified DAOs."""
    try:
        logger.info(f"Processing updates request for DAOs: {request.dao_slugs}")
        
        # Get DaoUpdatesAgent instance
        agent = get_updates_agent()
        logger.info("DAO Updates Agent initialized successfully")
        
        # Get updates for each DAO
        all_updates = []
        for dao_slug in request.dao_slugs:
            try:
                updates = await agent.get_dao_updates(
                    dao_slug=dao_slug,
                    user_holdings=request.token_holdings
                )
                logger.info(f"Got {len(updates)} updates for DAO {dao_slug}")
                all_updates.extend(updates)
            except Exception as e:
                logger.error(f"Error getting updates for DAO {dao_slug}: {str(e)}")
                continue
        
        # Sort all updates by priority and timestamp
        sorted_updates = sorted(
            all_updates,
            key=lambda x: (
                {'urgent': 0, 'important': 1, 'fyi': 2}[x.priority],
                x.timestamp
            ),
            reverse=True
        )
        
        logger.info(f"Returning {len(sorted_updates)} total updates")
        return sorted_updates
        
    except Exception as e:
        logger.error(f"Error processing updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}