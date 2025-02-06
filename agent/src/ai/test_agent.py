# agent/src/ai/test_agent.py

import pytest
from .agent import TabulaAgent

@pytest.mark.asyncio
async def test_dao_summary():
    # Initialize with test credentials
    test_credentials = {
        "api_key_name": "test",
        "private_key": "test"
    }
    
    agent = TabulaAgent(test_credentials)
    
    # Test with Arbitrum DAO
    summary = await agent.get_dao_summary("arbitrum")
    
    assert summary is not None
    assert "raw_data" in summary
    assert "ai_summary" in summary
    
    # Add more specific assertions based on expected data structure