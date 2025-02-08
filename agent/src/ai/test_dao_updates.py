# agent/src/ai/test_dao_updates.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from .dao_updates import (
    DaoUpdatesAgent,
    DaoUpdate,
    ImpactAnalysis,
    SocialSentiment,
    TreasuryChange
)

class MockChatModel(BaseChatModel):
    """Mock LLM for testing."""
    
    def _generate(self, *args, **kwargs):
        response = MagicMock()
        response.content = """
Summary: This proposal has moderate impact on protocol parameters
Areas: Treasury, Governance
Risk: medium
"""
        return MagicMock(generations=[MagicMock(message=response)])

    def _llm_type(self):
        return "mock"

@pytest.fixture
def mock_tally_client():
    with patch('agent.src.tally.client.TallyClient') as mock:
        client = Mock()
        # Mock organization data
        client.get_organization.return_value = {
            'data': {
                'organization': {
                    'id': 'org_123',
                    'name': 'Test DAO',
                    'chainIds': ['eip155:8453'],
                    'proposalsCount': 5,
                    'delegatesCount': 100
                }
            }
        }
        # Mock proposals data
        client.get_proposals.return_value = {
            'data': {
                'proposals': {
                    'nodes': [
                        {
                            'id': 'prop_1',
                            'metadata': {
                                'title': 'Test Proposal',
                                'description': 'A test proposal for unit testing'
                            },
                            'status': 'active',
                            'voteStats': [
                                {
                                    'type': 'for',
                                    'votesCount': '1000000',
                                    'votersCount': 50,
                                    'percent': 75.5
                                }
                            ]
                        }
                    ]
                }
            }
        }
        mock.return_value = client
        return client

@pytest.fixture
def mock_cdp_wrapper():
    wrapper = Mock()
    # Mock toolkit and tools
    toolkit = Mock()
    wrapper.get_tools.return_value = []
    
    # Create a class mock that returns our pre-configured wrapper
    class_mock = Mock()
    class_mock.return_value = wrapper
    
    with patch('cdp_langchain.utils.CdpAgentkitWrapper', class_mock):
        yield wrapper

@pytest.fixture
def agent(mock_tally_client, mock_cdp_wrapper):
    # Create agent with test credentials
    agent = DaoUpdatesAgent(
        cdp_credentials={
            'cdp_api_key_name': 'test_key',
            'cdp_api_key_private_key': 'test_private_key'
        },
        llm=MockChatModel()
    )
    
    # Replace TallyClient with our mock
    agent.tally_client = mock_tally_client
    return agent

@pytest.mark.asyncio
async def test_get_dao_updates_basic(agent):
    """Test basic functionality of get_dao_updates."""
    updates = await agent.get_dao_updates('test-dao')
    
    assert isinstance(updates, list)
    assert len(updates) > 0
    
    # Check first update structure
    first_update = updates[0]
    assert isinstance(first_update, DaoUpdate)
    assert first_update.dao_slug == 'test-dao'
    assert first_update.priority in ['urgent', 'important', 'fyi']
    assert first_update.category in ['proposal', 'treasury', 'governance', 'social']

@pytest.mark.asyncio
async def test_proposal_impact_analysis(agent):
    """Test proposal impact analysis."""
    proposal_data = {
        'metadata': {
            'title': 'Test Proposal',
            'description': 'A test proposal that would change treasury parameters'
        }
    }
    
    impact = agent._analyze_proposal_impact(proposal_data)
    
    assert isinstance(impact, ImpactAnalysis)
    assert impact.summary != ""
    assert len(impact.affected_areas) > 0
    assert impact.risk_level in ['low', 'medium', 'high']

@pytest.mark.asyncio
async def test_social_sentiment_analysis(agent):
    """Test social sentiment analysis."""
    sentiment = agent._get_social_sentiment('test-dao')
    
    assert isinstance(sentiment, SocialSentiment)
    assert -1 <= sentiment.score <= 1
    assert len(sentiment.trending_keywords) > 0
    assert sentiment.total_mentions >= 0

@pytest.mark.asyncio
async def test_treasury_analysis(agent):
    """Test treasury change analysis."""
    treasury_data = {
        'balance': '1000000',
        'token_symbol': 'TEST',
        'previous_balance': '900000'
    }
    
    analysis = agent._analyze_treasury_change(treasury_data)
    
    assert isinstance(analysis, dict)
    assert 'summary' in analysis
    assert 'priority' in analysis
    assert 'details' in analysis
    assert isinstance(analysis['details'], TreasuryChange)

@pytest.mark.asyncio
async def test_error_handling(agent, mock_tally_client):
    """Test error handling when API calls fail."""
    mock_tally_client.get_organization.side_effect = Exception("API Error")
    
    updates = await agent.get_dao_updates('test-dao')
    assert isinstance(updates, list)
    assert len(updates) == 0

@pytest.mark.asyncio
async def test_timestamp_format(agent):
    """Test that timestamps are in correct ISO format."""
    updates = await agent.get_dao_updates('test-dao')
    
    for update in updates:
        try:
            timestamp = datetime.fromisoformat(update.timestamp.replace('Z', '+00:00'))
            assert timestamp.tzinfo == timezone.utc
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {update.timestamp}")