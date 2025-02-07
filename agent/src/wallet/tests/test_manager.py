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
async def test_dao_involvement():
    # Load environment variables
    load_dotenv()
    
    manager = WalletManager()
    test_address = "0x746bb7beFD31D9052BB8EbA7D5dD74C9aCf54C6d"
    
    result = await manager.get_dao_involvement(test_address)
    
    # Basic structure tests
    assert result is not None
    assert "active_delegations" in result
    assert "potential_daos" in result
    assert "error" in result
    
    # Print results regardless of test status
    print("\nDAO Involvement Test Results:")
    if result["error"] is None:
        print("\nActive Delegations:")
        for delegation in result["active_delegations"]:
            print(f"- {delegation['dao_name']} ({delegation['dao_slug']})")
            if 'delegation_info' in delegation:
                print(f"  Delegation details: {delegation['delegation_info']}")
        
        print("\nPotential DAOs:")
        for dao in result["potential_daos"]:
            print(f"- {dao['dao_name']} ({dao['dao_slug']})")
            if 'activity' in dao and 'nodes' in dao['activity']:
                print(f"  Activity found: {len(dao['activity']['nodes'])} interactions")
    else:
        print(f"\nError encountered: {result['error']}")
    
    return result  # Return for additional assertions if needed

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_dao_involvement())