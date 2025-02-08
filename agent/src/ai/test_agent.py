# agent/src/ai/test_agent.py

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

# Load .env from project root
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Import the agent - using relative imports
from chatbot_agent import DAOGovernanceAgent

async def test_agent():
    """Test the DAO Governance Agent with various scenarios."""
    print("\nLoading environment variables from:", env_path)
    print("Environment variables status:")
    for var in ['OPENAI_API_KEY', 'CDP_API_KEY_NAME', 'CDP_API_KEY_PRIVATE_KEY', 'TALLY_API_KEY']:
        print(f"{var} is {'set' if os.getenv(var) else 'not set'}")

    print("\nInitializing DAO Governance Agent...")
    agent = DAOGovernanceAgent()
    
    # Test cases
    test_messages = [
        "What's my wallet address?",
        "Show me all Base DAOs available",
        "What are the recent proposals for Uniswap?",
        "How do I delegate my tokens?",
        "Show me the treasury allocation for Base",
    ]
    
    print("\nStarting test cases...")
    for message in test_messages:
        print(f"\n🔹 Testing: {message}")
        try:
            response = await agent.chat(message)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    # Test onchain action
    print("\n🔹 Testing onchain action: Request faucet funds")
    try:
        response = await agent.chat("Can you request some test tokens from the faucet?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_agent())