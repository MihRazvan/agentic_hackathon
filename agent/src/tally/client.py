import os
from typing import Dict, Any, Optional, List
import requests
from dotenv import load_dotenv
import json

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

    def get_dao_metadata(self, organization_id: str) -> Dict[str, Any]:
        """Gets basic DAO information like treasury size, holders, etc."""
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
                metadata {
                    description
                    icon
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
        """Gets active proposals for a DAO with proper fragment handling."""
        query = """
        query GetActiveProposals($input: ProposalsInput!) {
            proposals(input: $input) {
                nodes {
                    ... on Proposal {
                        id
                        metadata {
                            title
                            description
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
        return self._execute_query(query, variables)

    def get_historical_proposals(self, organization_id: str, limit: int = 10) -> Dict[str, Any]:
        """Gets historical proposals for analysis."""
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
                            percent
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
        """Gets delegation info for an address in a specific DAO."""
        query = """
        query GetDelegate($input: DelegateInput!) {
            delegate(input: $input) {
                delegatorsCount
                votesCount
                governor {
                    name
                    tokenId
                }
                organization {
                    name
                    proposalsCount
                }
                token {
                    symbol
                    name
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

    def get_delegates(self, organization_id: str, limit: int = 10) -> Dict[str, Any]:
        """Gets list of delegates for a DAO."""
        query = """
        query GetDelegates($input: DelegatesInput!) {
            delegates(input: $input) {
                nodes {
                    ... on Delegate {
                        account {
                            address
                            name
                        }
                        votesCount
                        delegatorsCount
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

    def _execute_query(self, query: str, variables: Dict) -> Dict:
        """Helper function to execute GraphQL queries with error handling."""
        try:
            response = requests.post(
                self.endpoint,
                json={
                    'query': query,
                    'variables': variables
                },
                headers=self.headers,
                timeout=10  # Add timeout
            )
            
            # Check if response is JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response")
                return None

            # Check for successful response
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

    # Helper methods for data analysis
    def format_proposal_stats(self, proposal_data: Dict) -> Dict[str, Any]:
        """Formats proposal statistics into a more readable format."""
        if not proposal_data or 'data' not in proposal_data:
            return {}
            
        formatted = {}
        try:
            if 'proposals' in proposal_data['data']:
                proposals = proposal_data['data']['proposals']['nodes']
                formatted['total_proposals'] = len(proposals)
                formatted['status_counts'] = {}
                formatted['vote_distribution'] = {}
                
                for proposal in proposals:
                    # Count statuses
                    status = proposal.get('status')
                    formatted['status_counts'][status] = formatted['status_counts'].get(status, 0) + 1
                    
                    # Analyze votes
                    vote_stats = proposal.get('voteStats', [])
                    for stat in vote_stats:
                        vote_type = stat.get('type')
                        if vote_type:
                            if vote_type not in formatted['vote_distribution']:
                                formatted['vote_distribution'][vote_type] = []
                            formatted['vote_distribution'][vote_type].append(float(stat.get('percent', 0)))
                            
                # Calculate averages for vote distributions
                for vote_type in formatted['vote_distribution']:
                    votes = formatted['vote_distribution'][vote_type]
                    formatted['vote_distribution'][vote_type] = {
                        'average': sum(votes) / len(votes) if votes else 0,
                        'count': len(votes)
                    }
                    
            return formatted
            
        except Exception as e:
            print(f"Error formatting proposal stats: {e}")
            return {}

    def get_key_daos(self) -> List[str]:
        """Returns a list of key DAOs on Arbitrum."""
        return [
            "arbitrum",
            "gmx-governance", 
            "jones-dao",
            "camelot",
            "radiant"
        ]