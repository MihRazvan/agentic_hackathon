# agent/src/ai/test_assistant.py

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
agent_dir = src_dir.parent
project_root = agent_dir.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Print environment variable status
print("\nEnvironment status:")
print(f"Loading .env from: {env_path}")
for var in ['OPENAI_API_KEY', 'TALLY_API_KEY']:
    print(f"{var} is {'set' if os.getenv(var) else 'not set'}")

from agent.src.ai.dao_assistant import DAOAssistant

async def test_assistant():
    """Test the DAO Assistant."""
    print("\nInitializing DAO Assistant...")
    assistant = DAOAssistant()
    
    # Test proposal analysis
    print("\n🔹 Testing proposal analysis for Seamless Protocol...")
    response = await assistant.get_proposal_analysis("seamless-protocol")
    print(f"Response: {response}")
    
    # Test delegate recommendations
    print("\n🔹 Testing delegate recommendations for Gloom...")
    response = await assistant.get_delegate_recommendations("gloom")
    print(f"Response: {response}")
    
    # Test treasury analysis
    print("\n🔹 Testing treasury analysis for Internet Token DAO...")
    response = await assistant.get_treasury_analysis("internet-token-dao")
    print(f"Response: {response}")
    
    # Test chat interface
    test_questions = [
        "Can you explain the latest Seamless Protocol proposal in simple terms?",
        "Who would you recommend as a delegate for Gloom based on their past performance?",
        "What's the current state of Internet Token DAO's treasury?",
        "If I want to delegate my Seamless tokens, what steps should I take?"
    ]
    
    print("\n🔹 Testing chat interface...")
    for question in test_questions:
        print(f"\nQ: {question}")
        response = await assistant.chat(question)
        print(f"A: {response}")
        await asyncio.sleep(2)  # Rate limiting

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_assistant())