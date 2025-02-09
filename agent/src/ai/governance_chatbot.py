import logging
import openai
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key in environment variables")

class GovernanceChatbot:
    def __init__(self):
        self.client = openai.ChatCompletion()

    def chat(self, user_input: str) -> str:
        """Handles chatbot responses, ensuring stability."""
        payload = {
            "model": "gpt-4-0125-preview",
            "messages": [{"role": "user", "content": user_input}],
            "temperature": 0.7
        }

        try:
            response = self.client.create(**payload)

            # ✅ Log full OpenAI response for debugging
            logging.info(f"OpenAI API Response: {response}")

            # ✅ Handle missing 'messages' key
            if "choices" not in response or not response["choices"]:
                logging.error("Unexpected OpenAI response format")
                return "Unexpected response from AI model."

            return response["choices"][0].get("message", {}).get("content", "No response available.")

        except openai.error.RateLimitError:
            logging.error("Rate limit exceeded. Try again later.")
            return "Rate limit exceeded. Please wait and try again."

        except openai.error.OpenAIError as e:
            logging.error(f"OpenAI API Error: {str(e)}")
            return "There was an issue processing your request."

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return "An unexpected error occurred."

