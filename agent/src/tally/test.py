# test.py
import json
from client import TallyClient

def test_tally_api():
    client = TallyClient()
    
    # Test getting DAO data for Arbitrum
    print("\nTesting DAO Info for Arbitrum:")
    dao_info = client.get_dao_metadata("arbitrum")
    print(json.dumps(dao_info, indent=2))

    if dao_info and 'data' in dao_info:
        org_id = dao_info['data']['organization']['id']
        
        # Test getting proposals
        print("\nTesting Active Proposals:")
        proposals = client.get_active_proposals(org_id)
        print(json.dumps(proposals, indent=2))
        
        # Test getting delegate info for a sample address
        print("\nTesting Delegate Info:")
        delegate = client.get_delegate_info("0xF7B2c6EC553da81F645f86E3CA38bE0d44bAEDf1", org_id)
        print(json.dumps(delegate, indent=2))

if __name__ == "__main__":
    test_tally_api()