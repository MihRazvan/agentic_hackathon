# agent/src/tally/client.py

from typing import Dict, List, Any
import requests
import json
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TallyClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('TALLY_API_KEY')
        if not self.api_key:
            raise ValueError("TALLY_API_KEY not found in environment variables")
            
        logger.info(f"Initialized TallyClient with API key: {self.api_key[:6]}...")
        
        self.endpoint = "https://api.tally.xyz/query"
        self.headers = {
            'Api-Key': self.api_key,
            'Content-Type': 'application/json',
        }
        
        # Known significant DAOs with their token IDs
        self.major_daos = {
            'arbitrum': {
                'slug': 'arbitrum',
                'token_id': 'eip155:42161/erc20:0x912CE59144191C1204E64559FE8253a0e49E6548'  # ARB token
            },
            'seamless-protocol': {
                'slug': 'seamless-protocol',
                'token_id': 'eip155:8453/erc20:0x1C7a460413dD4e964f96D8dFC56E7223cE88CD85'
            },
            'internet-token-dao': {
                'slug': 'internet-token-dao',
                'token_id': 'eip155:8453/erc20:0x968D6A288d7B024D5012c0B25d67A889E4E3eC19'
            },
            'gloom': {
                'slug': 'gloom',
                'token_id': 'eip155:8453/erc20:0xbb5D04c40Fa063FAF213c4E0B8086655164269Ef'
            }
        }

    def get_token_balance(self, address: str, token_id: str) -> Dict[str, Any]:
        """Gets token balance for an address."""
        logger.info(f"Getting token balance for address {address[:10]}... and token {token_id}")
        
        query = """
        query GetTokenBalance($address: AccountID!) {
            account(input: { id: $address }) {
                delegatesCount
                votesCount
                tokens {
                    balance
                    token {
                        id
                        type
                        name
                        symbol
                        decimals
                    }
                }
            }
        }
        """
        
        # Convert address to AccountID format
        chain_id = token_id.split('/')[0]  # e.g., 'eip155:42161'
        account_id = f"{chain_id}:{address}"
        
        variables = {
            "address": account_id
        }
        
        logger.info(f"Querying with account ID: {account_id}")
        result = self._execute_query(query, variables)
        
        if result and 'data' in result and 'account' in result['data']:
            account = result['data']['account']
            tokens = account.get('tokens', [])
            
            # Find the specific token we're looking for
            for token_data in tokens:
                token = token_data.get('token', {})
                if token.get('id') == token_id:
                    balance_info = {
                        'balance': float(token_data.get('balance', 0)),
                        'symbol': token.get('symbol', 'UNKNOWN'),
                        'decimals': token.get('decimals', 18)
                    }
                    logger.info(f"Found balance: {balance_info}")
                    return balance_info
            
            logger.warning(f"Token {token_id} not found in account's tokens")
            return {
                'balance': 0,
                'symbol': 'UNKNOWN',
                'decimals': 18
            }
        
        logger.warning(f"No token data found for {address[:10]}...")
        return {
            'balance': 0,
            'symbol': 'UNKNOWN',
            'decimals': 18
        }

    def get_organizations(self) -> Dict[str, Any]:
        """Gets list of significant mainnet organizations."""
        query = """
        query Organizations($input: OrganizationsInput) {
            organizations(input: $input) {
                nodes {
                    ... on Organization {
                        id
                        slug
                        name
                        chainIds
                        tokenIds
                        governorIds
                        metadata {
                            description
                            icon
                        }
                        hasActiveProposals
                        proposalsCount
                        delegatesCount
                        delegatesVotesCount
                        tokenOwnersCount
                    }
                }
            }
        }
        """
        
        all_daos = {
            "data": {
                "organizations": {
                    "nodes": []
                }
            }
        }

        # Get Arbitrum DAO specifically
        logger.info("Fetching Arbitrum DAO...")
        arbitrum_query = """
        query GetArbitrumDAO {
            organization(input: { slug: "arbitrum" }) {
                id
                slug
                name
                chainIds
                tokenIds
                governorIds
                metadata {
                    description
                    icon
                }
                hasActiveProposals
                proposalsCount
                delegatesCount
                delegatesVotesCount
                tokenOwnersCount
            }
        }
        """
        arbitrum_result = self._execute_query(arbitrum_query, {})
        if arbitrum_result and 'data' in arbitrum_result and 'organization' in arbitrum_result['data']:
            arbitrum_dao = arbitrum_result['data']['organization']
            if arbitrum_dao:
                # Add ARB token ID if not present
                if not arbitrum_dao.get('tokenIds'):
                    arbitrum_dao['tokenIds'] = [self.major_daos['arbitrum']['token_id']]
                all_daos["data"]["organizations"]["nodes"].append(arbitrum_dao)
                logger.info("Successfully found Arbitrum DAO")
        
        # Get other Arbitrum mainnet DAOs
        logger.info("Fetching other Arbitrum DAOs...")
        arbitrum_result = self._execute_query(query, {
            "input": {
                "filters": {
                    "chainId": "eip155:42161"
                }
            }
        })
        
        # Get Base mainnet DAOs
        logger.info("Fetching Base DAOs...")
        base_result = self._execute_query(query, {
            "input": {
                "filters": {
                    "chainId": "eip155:8453"
                }
            }
        })
        
        if arbitrum_result and 'data' in arbitrum_result:
            all_daos["data"]["organizations"]["nodes"].extend(
                arbitrum_result["data"]["organizations"]["nodes"]
            )
            
        if base_result and 'data' in base_result:
            all_daos["data"]["organizations"]["nodes"].extend(
                base_result["data"]["organizations"]["nodes"]
            )
            
        # Add token IDs for major DAOs if missing
        for node in all_daos["data"]["organizations"]["nodes"]:
            if node.get('slug') in self.major_daos:
                if not node.get('tokenIds'):
                    node['tokenIds'] = [self.major_daos[node['slug']]['token_id']]
        
        return all_daos

    def get_organization(self, organization_id: str) -> Dict[str, Any]:
        """Gets comprehensive organization information."""
        query = """
        query GetDAOData($input: OrganizationInput!) {
            organization(input: $input) {
                id
                name
                chainIds 
                proposalsCount
                delegatesCount
                tokenOwnersCount
                hasActiveProposals
                governorIds
                tokenIds
                metadata {
                    description
                    icon
                    color
                }
            }
        }
        """
        
        variables = {
            "input": {
                "slug": organization_id
            }
        }
        return self._execute_query(query, variables)

    def _execute_query(self, query: str, variables: Dict) -> Dict:
        """Enhanced helper function to execute GraphQL queries."""
        try:
            logger.debug(f"Executing query with variables: {variables}")
            
            response = requests.post(
                self.endpoint,
                json={
                    'query': query,
                    'variables': variables
                },
                headers=self.headers,
                timeout=10
            )
            
            try:
                data = response.json()
                if 'errors' in data:
                    logger.error(f"GraphQL Errors: {data['errors']}")
                    return None
                return data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response.text}")
                return None

            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None