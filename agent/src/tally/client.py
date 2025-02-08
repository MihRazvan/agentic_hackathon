# agent/src/tally/client.py

from typing import Dict, List, Any
import requests
import json
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
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
        
        # Known significant Base DAOs
        self.major_daos = {
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

    def get_organizations(self) -> Dict[str, Any]:
        """Gets list of Base organizations."""
        logger.info("Fetching Base DAOs...")
        
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
        
        # Get Base mainnet DAOs
        result = self._execute_query(query, {
            "input": {
                "filters": {
                    "chainId": "eip155:8453"  # Base mainnet
                }
            }
        })
        
        if not result or 'data' not in result:
            logger.error("Failed to fetch Base DAOs")
            return {"data": {"organizations": {"nodes": []}}}
        
        # Add token IDs for major DAOs if missing
        for node in result['data']['organizations']['nodes']:
            if node.get('slug') in self.major_daos:
                if not node.get('tokenIds'):
                    node['tokenIds'] = [self.major_daos[node['slug']]['token_id']]
        
        logger.info(f"Found {len(result['data']['organizations']['nodes'])} Base DAOs")
        return result

    def get_delegate_info(self, address: str, organization_id: str) -> Dict[str, Any]:
        """Gets delegation information for an address in a DAO."""
        query = """
        query GetDelegate($input: DelegateInput!) {
            delegate(input: $input) {
                delegatorsCount
                votesCount
                account {
                    address
                    name
                    ens
                }
                governor {
                    name
                    tokenId
                    type
                }
                organization {
                    name
                    proposalsCount
                }
                token {
                    symbol
                    name
                    supply
                }
            }
        }
        """
        
        variables = {
            "input": {
                "address": address,
                "organizationId": organization_id
            }
        }
        
        result = self._execute_query(query, variables)
        if result and 'data' in result and 'delegate' in result['data']:
            return result['data']['delegate']
        return None

    def get_organization(self, organization_id: str) -> Dict[str, Any]:
        """Gets comprehensive DAO information."""
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

    def get_proposals(self, organization_id: str, include_active: bool = True) -> Dict[str, Any]:
        """Gets all or active proposals for a DAO."""
        query = """
        query GetProposals($input: ProposalsInput!) {
            proposals(input: $input) {
                nodes {
                    ... on Proposal {
                        id
                        metadata {
                            title
                            description
                        }
                        status
                        voteStats {
                            type
                            votesCount
                            votersCount
                            percent
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "filters": {
                    "organizationId": organization_id
                }
            }
        }
        
        if include_active:
            variables["input"]["filters"]["status"] = "active"
            
        return self._execute_query(query, variables)

    def _execute_query(self, query: str, variables: Dict) -> Dict:
        """Helper function to execute GraphQL queries."""
        try:
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
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return None