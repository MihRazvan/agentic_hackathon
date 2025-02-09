import time
from agent.src.ai.governance_chatbot import GovernanceChatbot

# Initialize chatbot
bot = GovernanceChatbot()

# Test Cases
test_cases = [
    ("🔹 TEST 1: DAO Information", "dao seamless-protocol"),
    ("🔹 TEST 2: Basic AI Chat", "What is the purpose of governance tokens?"),
    ("🔹 TEST 3: Proposal Analysis", "Break down the implications of Proposal 7 in Seamless Protocol."),
    ("🔹 TEST 4: DAO Treasury Info", "Show me Seamless Protocol's treasury allocation."),
    ("🔹 TEST 5: Delegate Assistance", "Help me choose the best delegate for Gloom DAO.")
]

# Run tests
for test_name, query in test_cases:
    print(f"\n{test_name}")
    try:
        response = bot.chat(query)
        print(response)
    except Exception as e:
        print(f"❌ ERROR in {test_name}: {e}")

    time.sleep(2)  # ✅ Delay to avoid rate limiting
