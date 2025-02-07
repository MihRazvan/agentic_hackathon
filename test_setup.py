import os
from dotenv import load_dotenv
from cdp import Cdp
from agent.src.ai.agent import TabulaAgent
from agent.src.tally.client import TallyClient

def test_environment():
    print("Testing environment setup...")
    
    # Test environment variables
    load_dotenv()
    
    required_vars = [
        'CDP_API_KEY_NAME',
        'CDP_API_KEY_PRIVATE_KEY',
        'OPENAI_API_KEY',  
        'TALLY_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Missing environment variables: {missing_vars}")
        return False
        
    # Test CDP SDK configuration
    try:
        Cdp.configure(
            os.getenv('CDP_API_KEY_NAME'),
            os.getenv('CDP_API_KEY_PRIVATE_KEY')
        )
        print("✅ CDP SDK configured successfully")
    except Exception as e:
        print(f"❌ CDP SDK configuration failed: {e}")
        return False
    
    # Test Tally client
    try:
        tally = TallyClient()
        test_dao = tally.get_dao_metadata("arbitrum")
        if test_dao:
            print("✅ Tally API working successfully")
    except Exception as e:
        print(f"❌ Tally API test failed: {e}")
        return False
    
    # Test Agent initialization
    try:
        credentials = {
            "api_key_name": os.getenv('CDP_API_KEY_NAME'),
            "private_key": os.getenv('CDP_API_KEY_PRIVATE_KEY')
        }
        agent = TabulaAgent(credentials)
        print("✅ TabulaAgent initialized successfully")
    except Exception as e:
        print(f"❌ TabulaAgent initialization failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_environment():
        print("\n🎉 All systems operational!")
    else:
        print("\n❌ Setup incomplete - check errors above")