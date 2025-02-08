# test_tally_integration.py

import asyncio
import logging
from agent.src.tally.client import TallyClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_tally_integration():
    """Test Tally API integration with detailed logging."""
    try:
        client = TallyClient()
        test_address = "0x8F9DF4115ac301d0e7dd087c270C2282fC7336ab"  # Your address

        # Test 1: Get Organizations
        logger.info("\n=== Testing Organization Fetching ===")
        orgs = client.get_organizations()
        
        arbitrum_daos = []
        base_daos = []
        
        if orgs and 'data' in orgs and 'organizations' in orgs['data']:
            nodes = orgs['data']['organizations']['nodes']
            
            # Split DAOs by chain
            for org in nodes:
                if 'eip155:42161' in org.get('chainIds', []):
                    arbitrum_daos.append(org)
                if 'eip155:8453' in org.get('chainIds', []):
                    base_daos.append(org)
            
            logger.info(f"\nFound {len(arbitrum_daos)} Arbitrum DAOs")
            logger.info(f"Found {len(base_daos)} Base DAOs")
            
            # Check for Arbitrum in particular
            arbitrum_dao = next((dao for dao in nodes if dao.get('slug') == 'arbitrum'), None)
            if arbitrum_dao:
                logger.info("\nArbitrum DAO Details:")
                logger.info(f"Name: {arbitrum_dao.get('name')}")
                logger.info(f"Delegates: {arbitrum_dao.get('delegatesCount')}")
                logger.info(f"Token IDs: {arbitrum_dao.get('tokenIds', [])}")
                
                # Test token balance if we found Arbitrum's token ID
                if arbitrum_dao.get('tokenIds'):
                    arb_token_id = arbitrum_dao['tokenIds'][0]  # Usually the first token
                    logger.info(f"\nChecking ARB balance for address {test_address}")
                    balance = client.get_token_balance(test_address, arb_token_id)
                    if balance:
                        logger.info(f"ARB Balance: {balance.get('balance')} {balance.get('symbol')}")
                    else:
                        logger.info("No ARB balance found")
            else:
                logger.warning("Arbitrum DAO not found in the results")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_tally_integration())