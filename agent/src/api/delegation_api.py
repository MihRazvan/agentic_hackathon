# agent/src/api/delegation_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import logging
from ..tally.client import TallyClient
from ..ai.dao_updates import DaoUpdatesAgent, DaoUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.post("/api/delegations/{address}")
async def get_delegations(address: str, request: DelegationRequest):
    """Get delegations for a wallet address based on token holdings."""
    logger.info(f"Processing delegations for address: {address}")
    logger.info(f"Token holdings: {request.token_holdings}")
    
    try:
        # Initialize Tally client
        tally_client = TallyClient()
        
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
        logger.info(f"Processing updates for DAOs: {request.dao_slugs}")
        
        # Initialize the DAO Updates Agent
        agent = DaoUpdatesAgent(cdp_credentials={
            # Add your CDP credentials here
            "api_key_name": "your_key_name",
            "api_key_private_key": "your_private_key"
        })
        
        all_updates = []
        for dao_slug in request.dao_slugs:
            updates = await agent.get_dao_updates(
                dao_slug=dao_slug,
                user_holdings=request.token_holdings
            )
            all_updates.extend(updates)
            
        # Sort all updates by priority and timestamp
        sorted_updates = sorted(all_updates, key=lambda x: (
            {'urgent': 0, 'important': 1, 'fyi': 2}[x.priority],
            x.timestamp
        ), reverse=True)
        
        logger.info(f"Returning {len(sorted_updates)} updates")
        return sorted_updates
        
    except Exception as e:
        logger.error(f"Error processing updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}