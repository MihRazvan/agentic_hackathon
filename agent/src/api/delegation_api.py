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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/delegations/{address}")
async def get_delegations(address: str):
    """Get delegations for a wallet address."""
    logger.info(f"Received request for address: {address}")
    
    try:
        # Initialize WalletManager
        wallet_manager = WalletManager()
        
        # Get DAO involvement
        logger.info(f"Fetching DAO involvement for {address}")
        result = await wallet_manager.get_dao_involvement(address)
        logger.info(f"Raw result: {result}")
        
        # Process potential DAOs
        active_delegations = result.get('active_delegations', [])
        potential_daos = result.get('potential_daos', [])
        
        # Get recommended DAOs - take the top 3 most active
        recommended = sorted(
            potential_daos,
            key=lambda x: (x.get('proposals_count', 0), x.get('delegates_count', 0)),
            reverse=True
        )[:3] if potential_daos else []
        
        response_data = {
            "active_delegations": active_delegations,
            "potential_daos": potential_daos,
            "recommended_delegations": recommended
        }
        
        logger.info(f"Returning response: {response_data}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing delegations for {address}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}