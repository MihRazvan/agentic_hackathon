# Tabula - Local Testing Guide

This guide explains how to test the three agents that power Tabula locally.

## Prerequisites

```bash
# Required Python version
Python 3.10+

# Required API Keys
- OPENAI_API_KEY
- CDP_API_KEY_NAME
- CDP_API_KEY_PRIVATE_KEY
- TALLY_API_KEY
```

## Setup Environment

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file in project root:
```env
OPENAI_API_KEY=your_key
CDP_API_KEY_NAME=your_key
CDP_API_KEY_PRIVATE_KEY=your_key
TALLY_API_KEY=your_key
```

## Testing Individual Agents

### 1. Tally Agent (DAO Data & Analytics)
Test the Tally API integration and data analytics:

```bash
# Run Tally agent tests
python agent/src/ai/test_tally_agent.py

Expected output:
✓ Successfully fetched Base DAOs
✓ Successfully fetched delegate data
✓ Successfully fetched proposal data
```

### 2. Alchemist Chatbot Agent
Test the natural language interaction capabilities:

```bash
# Run chatbot tests
python agent/src/ai/test_chatbot.py

Example commands to test:
- "Analyze the latest Seamless Protocol proposal"
- "Help me understand delegation in Gloom DAO"
- "What's the treasury status of Internet Token DAO?"
```

### 3. LLM Updates Curator Agent
Test the update curation and prioritization:

```bash
# Run curator tests
python agent/src/ai/test_updates_agent.py

Expected results:
- Updates should be categorized (urgent/important/fyi)
- Each update should have impact analysis
- Priority scoring should be consistent
```

## Testing API Layer

1. Start the FastAPI server:
```bash
uvicorn agent.src.api.main:app --reload --port 8000
```

2. Test endpoints using curl:
```bash
# Test chat endpoint
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze Seamless Protocol proposal #1"}'

# Test updates endpoint
curl -X POST "http://localhost:8000/api/updates" \
  -H "Content-Type: application/json" \
  -d '{"dao_slugs": ["seamless-protocol"]}'

# Test delegations endpoint
curl -X POST "http://localhost:8000/api/delegations/0x..." \
  -H "Content-Type: application/json" \
  -d '{"token_holdings": []}'
```

## Testing Frontend Integration

1. Start the frontend development server:
```bash
cd frontend
npm install
npm run dev
```

2. Open browser to `http://localhost:3000`

3. Test following flows:
- Connect wallet using OnchainKit
- View DAO updates
- Chat with governance assistant
- Check delegation recommendations

## Common Issues & Troubleshooting

1. API Key Issues:
```
Error: API key not found
Solution: Double-check .env file and key validity
```

2. Rate Limiting:
```
Error: Too many requests
Solution: Implement delay between requests in tests
```

3. Data Consistency:
```
Error: Inconsistent response formats
Solution: Ensure all agents return standardized response objects
```

## Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Check individual agents
python agent/src/ai/test_agent_health.py
```

## Note on Alchemist Agent Testing

Since the Alchemist Agent is deployed on Autonome, you can test it two ways:

1. Local Development:
```bash
# Test using local AgentKit
python agent/src/ai/test_alchemist_agent.py
```

2. Production Testing:
```bash
# Test deployed endpoint
curl -X POST "https://autonome.alt.technology/your-agent-url/poke" \
  -H "Content-Type: application/json" \
  -d '{"text": "Explain the latest Seamless proposal"}'
```

Remember that local tests use test API keys while production uses the keys configured in Autonome.
