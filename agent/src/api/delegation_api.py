# agent/src/api/delegation_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from ..tally.client import TallyClient

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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}