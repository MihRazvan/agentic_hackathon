# agent/src/tally/client.py

from typing import Dict, List, Any
import requests
import json
from dotenv import load_dotenv
import os

class TallyClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('TALLY_API_KEY')
        if not self.api_key:
            raise ValueError("TALLY_API_KEY not found in environment variables")
            
        self.endpoint = "https://api.tally.xyz/query"
        self.headers = {
            'Api-Key': self.api_key,
            'Content-Type': 'application/json',
        }

# agent/src/tally/client.py

from typing import Dict, List, Any
import requests
import json
from dotenv import load_dotenv
import os

class TallyClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('TALLY_API_KEY')
        if not self.api_key:
            raise ValueError("TALLY_API_KEY not found in environment variables")
            
        self.endpoint = "https://api.tally.xyz/query"
        self.headers = {
            'Api-Key': self.api_key,
            'Content-Type': 'application/json',
        }
        
        # Known significant DAOs
        self.major_daos = [
            'seamless-protocol',
            'internet-token-dao',
            'gloom',
            'uxd-arbitrum-one-council',
            'cora-protocol-dao',
            'wormhole'
        ]

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
                        creator {
                            address
                        }
                    }
                }
                pageInfo {
                    firstCursor
                    lastCursor
                    count
                }
            }
        }
        """
        
        # Get Arbitrum mainnet DAOs
        arbitrum_result = self._execute_query(query, {
            "input": {
                "filters": {
                    "chainId": "eip155:42161"  # Arbitrum mainnet
                }
            }
        })
        
        # Get Base mainnet DAOs
        base_result = self._execute_query(query, {
            "input": {
                "filters": {
                    "chainId": "eip155:8453"  # Base mainnet
                }
            }
        })
        
        # Combine results
        all_daos = {
            "data": {
                "organizations": {
                    "nodes": []
                }
            }
        }
        
        if arbitrum_result and 'data' in arbitrum_result:
            all_daos["data"]["organizations"]["nodes"].extend(
                arbitrum_result["data"]["organizations"]["nodes"]
            )
            
        if base_result and 'data' in base_result:
            all_daos["data"]["organizations"]["nodes"].extend(
                base_result["data"]["organizations"]["nodes"]
            )
            
        return all_daos

    def get_dao_metadata(self, organization_id: str) -> Dict[str, Any]:
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

    def get_active_proposals(self, organization_id: str) -> Dict[str, Any]:
        """Gets active proposals with comprehensive details."""
        query = """
        query GetActiveProposals($input: ProposalsInput!) {
            proposals(input: $input) {
                nodes {
                    ... on Proposal {
                        id
                        metadata {
                            title
                            description
                            ipfsHash
                        }
                        status
                        start {
                            ... on Block {
                                timestamp
                            }
                            ... on BlocklessTimestamp {
                                timestamp
                            }
                        }
                        end {
                            ... on Block {
                                timestamp
                            }
                            ... on BlocklessTimestamp {
                                timestamp
                            }
                        }
                        voteStats {
                            type
                            votesCount
                            votersCount
                            percent
                        }
                        executableCalls {
                            calldata
                            signature
                            target
                            value
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
        return self._execute_query(query, variables)

    def get_historical_proposals(self, organization_id: str, limit: int = 10) -> Dict[str, Any]:
        """Gets historical proposals with detailed analytics."""
        query = """
        query GetProposals($input: ProposalsInput!) {
            proposals(input: $input) {
                nodes {
                    ... on Proposal {
                        id
                        metadata {
                            title
                            description
                            ipfsHash
                        }
                        status
                        voteStats {
                            type
                            votesCount
                            votersCount
                            percent
                        }
                        creator {
                            address
                            name
                        }
                        events {
                            type
                            createdAt
                        }
                    }
                }
                pageInfo {
                    firstCursor
                    lastCursor
                    count
                }
            }
        }
        """
        
        variables = {
            "input": {
                "filters": {
                    "organizationId": organization_id
                },
                "page": {
                    "limit": limit
                }
            }
        }
        return self._execute_query(query, variables)

    def get_delegate_info(self, address: str, organization_id: str) -> Dict[str, Any]:
        """Gets comprehensive delegation information."""
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
                statement {
                    statement
                    isSeekingDelegation
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
        return self._execute_query(query, variables)

    def _execute_query(self, query: str, variables: Dict) -> Dict:
        """Enhanced helper function to execute GraphQL queries."""
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
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response")
                return None

            if response.status_code == 200:
                if 'errors' in data:
                    print(f"GraphQL Errors: {data['errors']}")
                    return None
                return data
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None
                
        except requests.exceptions.Timeout:
            print("Error: Request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error executing query: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None