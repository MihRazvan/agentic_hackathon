import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

API_KEY = os.getenv('TALLY_API_KEY')
ENDPOINT = "https://api.tally.xyz/query"

# GraphQL query
query = """
query GetDAOData($input: OrganizationInput!) {
    organization(input: $input) {
        id
        name
        chainIds
        proposalsCount
        hasActiveProposals
        delegatesCount
        tokenOwnersCount
    }
}
"""

# Variables for the query
variables = {
    "input": {
        "slug": "arbitrum"
    }
}

# Headers including the API key
headers = {
    'Api-Key': API_KEY,
    'Content-Type': 'application/json',
}

def test_tally_api():
    try:
        response = requests.post(
            ENDPOINT,
            json={
                'query': query,
                'variables': variables
            },
            headers=headers
        )
        
        if response.status_code == 200:
            print("Success! Response:")
            print(response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tally_api()