# agent/src/wallet/tests/test_manager.py

import os
import sys
import pytest
from dotenv import load_dotenv

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, project_root)

from agent.src.wallet.manager import WalletManager

@pytest.mark.asyncio
async def test_wallet_manager_initialization():
    """Test WalletManager initialization and DAO listing."""
    manager = WalletManager()
    
    # Test that we got some networks
    assert manager.supported_networks is not None
    assert len(manager.supported_networks) > 0
    
    # Verify we have major DAOs
    major_daos = manager.tally_client.major_daos
    found_daos = [slug for slug in manager.supported_networks.keys() if slug in major_daos]
    assert len(found_daos) > 0, "No major DAOs found"
    
    print(f"\nFound {len(found_daos)} major DAOs out of {len(manager.supported_networks)} total DAOs")

@pytest.mark.asyncio
async def test_chain_filtering():
    """Test filtering DAOs by chain."""
    manager = WalletManager()
    
    # Test Arbitrum filtering
    arbitrum_daos = manager.filter_supported_networks("eip155:42161")
    print("\nArbitrum DAOs:")
    for slug, data in arbitrum_daos.items():
        if data['delegates_count'] >= 50 or data['proposals_count'] >= 10:
            print(f"- {data['name']} ({slug})")
            print(f"  Delegates: {data['delegates_count']}")
            print(f"  Proposals: {data['proposals_count']}")
    
    # Test Base filtering
    base_daos = manager.filter_supported_networks("eip155:8453")
    print("\nBase DAOs:")
    for slug, data in base_daos.items():
        if data['delegates_count'] >= 50 or data['proposals_count'] >= 10:
            print(f"- {data['name']} ({slug})")
            print(f"  Delegates: {data['delegates_count']}")
            print(f"  Proposals: {data['proposals_count']}")

    # Verify we have DAOs on both chains
    assert len(arbitrum_daos) > 0, "No Arbitrum DAOs found"
    assert len(base_daos) > 0, "No Base DAOs found"

@pytest.mark.asyncio
async def test_dao_involvement():
    """Test getting DAO involvement for a specific address."""
    load_dotenv()
    
    manager = WalletManager()
    test_address = "0x746bb7beFD31D9052BB8EbA7D5dD74C9aCf54C6d"
    
    # Test without chain filter
    result = await manager.get_dao_involvement(test_address)
    
    # Basic structure tests
    assert result is not None
    assert "active_delegations" in result
    assert "potential_daos" in result
    assert "user_info" in result
    
    # Print results
    print("\nDAO Involvement Test Results:")
    print(f"\nUser Info:")
    print(f"Address: {result['user_info']['address']}")
    print(f"ENS: {result['user_info']['ens']}")
    print(f"Name: {result['user_info']['name']}")
    
    print("\nActive Delegations:")
    for delegation in result["active_delegations"]:
        print(f"\n- {delegation['dao_name']} ({delegation['dao_slug']})")
        print(f"  Chains: {', '.join(delegation['chain_ids'])}")
        if 'token' in delegation:
            print(f"  Token: {delegation['token']['symbol']} ({delegation['token']['name']})")
        print(f"  Votes Count: {delegation.get('votes_count', 'N/A')}")
        print(f"  Delegators: {delegation.get('delegators_count', 'N/A')}")
        print(f"  Total Proposals: {delegation.get('proposals_count', 'N/A')}")
        print(f"  Has Active Proposals: {delegation.get('has_active_proposals', False)}")
    
    print("\nPotential DAOs:")
    for dao in result["potential_daos"]:
        print(f"\n- {dao['dao_name']} ({dao['dao_slug']})")
        print(f"  Chains: {', '.join(dao['chain_ids'])}")
        print(f"  Delegates Count: {dao['delegates_count']}")
        print(f"  Proposals Count: {dao['proposals_count']}")
        print(f"  Has Active Proposals: {dao['has_active_proposals']}")

@pytest.mark.asyncio
async def test_specific_dao_info():
    """Test getting detailed information about a specific DAO."""
    manager = WalletManager()
    
    # Test with a known significant DAO
    test_daos = ["wormhole", "seamless-protocol", "frax"]
    
    for dao_slug in test_daos:
        result = await manager.get_specific_dao_info(dao_slug)
        
        if result and "error" not in result:
            print(f"\nSuccessfully retrieved info for {dao_slug}:")
            print(f"Name: {result.get('basic_info', {}).get('name')}")
            print(f"Chain IDs: {result.get('basic_info', {}).get('chain_ids')}")
            print(f"Delegates: {result.get('basic_info', {}).get('delegates_count')}")
            print(f"Proposals: {result.get('basic_info', {}).get('proposals_count')}")
            
            if result.get('active_proposals'):
                print("\nActive Proposals:")
                for proposal in result['active_proposals']:
                    print(f"- {proposal.get('metadata', {}).get('title', 'No Title')}")
            break
    
    assert result is not None
    assert "error" not in result
    return result