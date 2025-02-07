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
    
    # Print available networks for manual verification
    print("\nSupported Networks Count:", len(manager.supported_networks))

@pytest.mark.asyncio
async def test_chain_filtering():
    """Test filtering DAOs by chain."""
    manager = WalletManager()
    
    # Test Arbitrum filtering
    arbitrum_daos = manager.filter_supported_networks("eip155:42161")  # Arbitrum chain ID
    print("\nArbitrum DAOs:")
    for slug, data in arbitrum_daos.items():
        print(f"- {data['name']} ({slug})")
    
    # Test Base filtering
    base_daos = manager.filter_supported_networks("eip155:8453")  # Base chain ID
    print("\nBase DAOs:")
    for slug, data in base_daos.items():
        print(f"- {data['name']} ({slug})")

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
    
    # Test with Arbitrum DAO
    result = await manager.get_specific_dao_info("arbitrum")
    
    assert result is not None
    assert "error" not in result
    
    print("\nSpecific DAO Info Test Results:")
    print("\nBasic Info:")
    for key, value in result["basic_info"].items():
        print(f"{key}: {value}")
    
    print("\nActive Proposals:")
    for proposal in result["active_proposals"]:
        print(f"\n- {proposal.get('metadata', {}).get('title', 'No Title')}")
        print(f"  Status: {proposal.get('status', 'Unknown')}")
        if proposal.get('voteStats'):
            print("  Vote Stats:")
            for stat in proposal['voteStats']:
                print(f"    {stat.get('type')}: {stat.get('votesCount')} votes ({stat.get('percent')}%)")

if __name__ == "__main__":
    import asyncio
    
    async def run_all_tests():
        print("\nRunning all tests...")
        await test_wallet_manager_initialization()
        await test_chain_filtering()
        await test_dao_involvement()
        await test_specific_dao_info()
    
    asyncio.run(run_all_tests())