# agent/src/api/delegation_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from ..wallet.manager import WalletManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tabula API", description="DAO Intelligence Hub API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DelegationResponse(BaseModel):
    """Schema for a single delegation response."""
    dao_name: str = Field(..., description="Name of the DAO")
    dao_slug: str = Field(..., description="Slug identifier of the DAO")
    token_amount: str = Field(..., description="Amount of tokens delegated/available")
    chain_ids: List[str] = Field(..., description="List of chain IDs where the DAO operates")
    votes_count: Optional[str] = Field(None, description="Number of votes")
    proposals_count: Optional[int] = Field(None, description="Number of proposals")
    has_active_proposals: Optional[bool] = Field(None, description="Whether the DAO has active proposals")

class DelegationsData(BaseModel):
    """Schema for the complete delegations response."""
    active_delegations: List[DelegationResponse]
    recommended_delegations: List[DelegationResponse]

@app.get("/", include_in_schema=False)
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Tabula API"}

@app.get("/api/delegations/{address}", response_model=DelegationsData)
async def get_delegations(address: str):
    """
    Get active and recommended delegations for a wallet address.
    
    Args:
        address: Ethereum wallet address
        
    Returns:
        DelegationsData containing active and recommended delegations
    """
    try:
        logger.info(f"Fetching delegations for address: {address}")
        wallet_manager = WalletManager()
        result = await wallet_manager.get_dao_involvement(address)
        
        # Format active delegations
        active_delegations = []
        for d in result['active_delegations']:
            try:
                active_delegations.append(
                    DelegationResponse(
                        dao_name=d['dao_name'],
                        dao_slug=d['dao_slug'],
                        token_amount=f"{d.get('token', {}).get('symbol', 'TOKEN')} {d.get('votes_count', '0')}",
                        chain_ids=d['chain_ids'],
                        votes_count=str(d.get('votes_count', '0')),
                        proposals_count=d.get('proposals_count', 0),
                        has_active_proposals=d.get('has_active_proposals', False)
                    )
                )
            except Exception as e:
                logger.error(f"Error processing active delegation {d['dao_name']}: {str(e)}")
                continue
        
        # Format recommended delegations
        recommended_delegations = []
        for d in result['potential_daos']:
            try:
                recommended_delegations.append(
                    DelegationResponse(
                        dao_name=d['dao_name'],
                        dao_slug=d['dao_slug'],
                        token_amount=f"Available: {d.get('delegates_count', '0')} delegates",
                        chain_ids=d['chain_ids'],
                        proposals_count=d.get('proposals_count', 0),
                        has_active_proposals=d.get('has_active_proposals', False)
                    )
                )
            except Exception as e:
                logger.error(f"Error processing recommended DAO {d['dao_name']}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed delegations. Active: {len(active_delegations)}, Recommended: {len(recommended_delegations)}")
        return DelegationsData(
            active_delegations=active_delegations,
            recommended_delegations=recommended_delegations
        )
        
    except Exception as e:
        logger.error(f"Error processing delegations for {address}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)