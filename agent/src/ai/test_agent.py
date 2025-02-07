# agent/src/ai/test_agent.py
import os
import pytest
from dotenv import load_dotenv
from agent.src.ai.agent import TabulaAgent

@pytest.mark.asyncio
async def test_dao_summary():
    # Load environment variables
    load_dotenv()
    
    # Get actual credentials from environment
    test_credentials = {
        "api_key_name": os.getenv('CDP_API_KEY_NAME'),
        "private_key": os.getenv('CDP_API_KEY_PRIVATE_KEY')
    }
    
    agent = TabulaAgent(test_credentials)
    
    # Test with Arbitrum DAO
    summary = await agent.get_dao_summary("arbitrum")
    
    # Basic structure tests
    assert summary is not None
    assert "raw_data" in summary
    assert "ai_summary" in summary or "error" in summary
    
    if "error" not in summary:
        # Data validation tests
        assert isinstance(summary["raw_data"]["dao"], dict)
        assert isinstance(summary["raw_data"]["proposals"], list)
        assert isinstance(summary["ai_summary"], str)
        
        # Print results for inspection
        print("\nDAO Summary Test Results:")
        print(f"DAO Info: {summary['raw_data']['dao']}")
        print(f"Number of processed proposals: {len(summary['raw_data']['proposals'])}")
        print(f"AI Summary: {summary['ai_summary'][:200]}...")
    else:
        print(f"\nError encountered: {summary['error']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_dao_summary())