# agent/src/api/tests/test_delegation_api.py

import pytest
from fastapi.testclient import TestClient
from ..delegation_api import app

client = TestClient(app)

def test_health_check():
    """Test the API health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Tabula API"}

@pytest.mark.asyncio
async def test_get_delegations():
    """Test the delegations endpoint with a known address."""
    test_address = "0x746bb7beFD31D9052BB8EbA7D5dD74C9aCf54C6d"
    response = client.get(f"/api/delegations/{test_address}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "active_delegations" in data
    assert "recommended_delegations" in data
    assert isinstance(data["active_delegations"], list)
    assert isinstance(data["recommended_delegations"], list)
    
    # Check delegation data structure
    if data["active_delegations"]:
        delegation = data["active_delegations"][0]
        assert "dao_name" in delegation
        assert "dao_slug" in delegation
        assert "token_amount" in delegation
        assert "chain_ids" in delegation
        print("\nActive Delegation Example:", delegation)
    
    if data["recommended_delegations"]:
        recommendation = data["recommended_delegations"][0]
        assert "dao_name" in recommendation
        assert "dao_slug" in recommendation
        assert "token_amount" in recommendation
        assert "chain_ids" in recommendation
        print("\nRecommended Delegation Example:", recommendation)

def test_invalid_address():
    """Test the API's error handling with an invalid address."""
    response = client.get("/api/delegations/0xinvalid")
    assert response.status_code == 500