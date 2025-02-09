import time
from agent.src.ai.governance_chatbot import GovernanceChatbot

# ✅ Initialize chatbot
bot = GovernanceChatbot()

def run_test(test_name, query):
    """Executes a chatbot query with logging and error handling."""
    print(f"\n🔹 TEST: {test_name}")
    try:
        response = bot.chat(query)
        print(response)
    except Exception as e:
        print(f"❌ ERROR in {test_name}: {str(e)}")

# ✅ Run tests with delays to avoid rate limits
run_test("DAO Information", "dao seamless-protocol")
time.sleep(2)

run_test("Basic AI Chat", "What is the purpose of governance tokens?")
time.sleep(2)

run_test("Proposal Analysis", "Break down the implications of Proposal 7 in Seamless Protocol.")
time.sleep(2)

run_test("DAO Treasury Info", "Show me Seamless Protocol's treasury allocation.")
time.sleep(2)

run_test("Delegate Assistance", "Help me choose the best delegate for Gloom DAO.")
