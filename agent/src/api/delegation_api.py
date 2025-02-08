# agent/src/api/delegation_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import re

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

def validate_eth_address(address: str) -> bool:
    """Validate Ethereum address format."""
    if not address:
        return False
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

@app.get("/api/delegations/{address}")
async def get_delegations(address: str):
    """
    Get active and recommended delegations for a wallet address.
    
    Args:
        address: Ethereum wallet address from frontend
    """
    # Log the received address
    logger.info(f"Received request for address: {address}")
    
    # Validate address format
    if not validate_eth_address(address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
    
    try:
        # Initialize WalletManager
        wallet_manager = WalletManager()
        
        # Get DAO involvement using the provided address
        result = await wallet_manager.get_dao_involvement(address)
        
        logger.info(f"Successfully fetched delegations for {address}")
        logger.debug(f"Found {len(result['active_delegations'])} active delegations")
        logger.debug(f"Found {len(result['potential_daos'])} potential DAOs")
        
        return {
            "active_delegations": result['active_delegations'],
            "available_delegations": [
                dao for dao in result['potential_daos']
                if dao.get('tokenOwnersCount', 0) > 0
            ],
            "recommended_delegations": sorted(
                result['potential_daos'],
                key=lambda x: (
                    x.get('proposals_count', 0), 
                    x.get('delegates_count', 0)
                ),
                reverse=True
            )[:3]
        }
        
    except Exception as e:
        logger.error(f"Error processing delegations for {address}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)