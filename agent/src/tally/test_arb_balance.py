# test_arb_balance.py

from agent.src.tally.client import TallyClient
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_arb_balance():
    try:
        client = TallyClient()
        address = "0x8F9DF4115ac301d0e7dd087c270C2282fC7336ab"
        arb_token = "eip155:42161/erc20:0x912CE59144191C1204E64559FE8253a0e49E6548"
        
        logger.info(f"\nChecking ARB balance for {address}")
        balance = client.get_token_balance(address, arb_token)
        
        if balance:
            logger.info(f"\nBalance information:")
            logger.info(f"Amount: {balance['balance']}")
            logger.info(f"Symbol: {balance['symbol']}")
            logger.info(f"Decimals: {balance['decimals']}")
            
            # If we have decimals, show the human-readable balance
            if 'decimals' in balance:
                human_balance = balance['balance'] / (10 ** balance['decimals'])
                logger.info(f"Human-readable balance: {human_balance} {balance['symbol']}")
        else:
            logger.warning("No balance information returned")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_arb_balance()