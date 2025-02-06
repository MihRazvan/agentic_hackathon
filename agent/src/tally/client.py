import os
from typing import Dict, Any, Optional, List
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

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

    def get_vote_participation_stats(self, organization_id: str, governor_id: str = None) -> Dict[str, Any]:
        """Gets comprehensive voting participation statistics."""
        query = """
        query GetVoteStats($input: VotesInput!) {
            votes(input: $input) {
                nodes {
                    ... on Vote {
                        amount
                        type
                        voter {
                            address
                            votes(governorId: $governorId)
                        }
                        proposal {
                            metadata {
                                title
                            }
                            status
                        }
                        block {
                            timestamp
                        }
                        reason
                    }
                }
                pageInfo {
                    count
                }
            }
        }
        """
        
        # If governor_id is not provided, let's get it from the organization
        if not governor_id:
            org_data = self.get_dao_metadata(organization_id)
            if org_data and 'data' in org_data and 'organization' in org_data['data']:
                governor_ids = org_data['data']['organization'].get('governorIds', [])
                if governor_ids:
                    governor_id = governor_ids[0]

        if not governor_id:
            print("No governor ID available for vote stats")
            return None

        variables = {
            "input": {
                "filters": {
                    "organizationId": organization_id
                }
            },
            "governorId": governor_id
        }
        return self._execute_query(query, variables)

    def get_token_info(self, organization_id: str) -> Dict[str, Any]:
        """Gets detailed token and treasury information."""
        query = """
        query GetTokenInfo($input: OrganizationInput!) {
            organization(input: $input) {
                tokenIds
                governorIds
            }
        }
        """
        variables = {
            "input": {
                "id": organization_id
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

    def get_delegation_history(self, address: str, organization_id: str) -> Dict[str, Any]:
        """Gets historical delegation data."""
        query = """
        query GetDelegationHistory($input: DelegationsInput!) {
            delegators(input: $input) {
                nodes {
                    ... on Delegation {
                        votes
                        blockTimestamp
                        delegator {
                            address
                            name
                        }
                        token {
                            symbol
                            name
                        }
                    }
                }
                pageInfo {
                    count
                }
            }
        }
        """
        variables = {
            "input": {
                "filters": {
                    "address": address,
                    "organizationId": organization_id
                }
            }
        }
        return self._execute_query(query, variables)

    def get_user_governance_activity(self, address: str, organization_id: str) -> Dict[str, Any]:
        """Gets comprehensive user participation data."""
        # First get proposals for the organization
        proposals_query = """
        query GetProposals($input: ProposalsInput!) {
            proposals(input: $input) {
                nodes {
                    ... on Proposal {
                        id
                    }
                }
            }
        }
        """
        proposals_vars = {
            "input": {
                "filters": {
                    "organizationId": organization_id
                }
            }
        }
        
        proposals_data = self._execute_query(proposals_query, proposals_vars)
        if not proposals_data or 'data' not in proposals_data:
            return None
            
        proposal_ids = [p['id'] for p in proposals_data['data']['proposals']['nodes']]
        
        # Then get votes for these proposals
        query = """
        query GetUserActivity($input: VotesInput!) {
            votes(input: $input) {
                nodes {
                    ... on Vote {
                        proposal {
                            metadata {
                                title
                            }
                            status
                            organization {
                                name
                            }
                        }
                        type
                        amount
                        reason
                        block {
                            timestamp
                        }
                    }
                }
                pageInfo {
                    count
                }
            }
        }
        """
        variables = {
            "input": {
                "filters": {
                    "voter": address,
                    "proposalIds": proposal_ids
                }
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

    def aggregate_dao_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Aggregates comprehensive DAO analytics."""
        try:
            # Gather all relevant data
            dao_info = self.get_dao_metadata(organization_id)
            if not dao_info or 'data' not in dao_info or not dao_info['data'].get('organization'):
                print("Organization not found or invalid organization ID")
                return {}
                
            proposals = self.get_historical_proposals(organization_id)
            token_info = self.get_token_info(organization_id)
            
            if not all([proposals, token_info]):
                return {}
            
            # Process vote statistics
            votes_data = vote_stats.get('data', {}).get('votes', {}).get('nodes', [])
            vote_types = {}
            participation_over_time = {}
            
            for vote in votes_data:
                vote_type = vote.get('type')
                timestamp = vote.get('block', {}).get('timestamp')
                if vote_type and timestamp:
                    vote_types[vote_type] = vote_types.get(vote_type, 0) + 1
                    date = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                    participation_over_time[date] = participation_over_time.get(date, 0) + 1
            
            # Combine all analytics
            analytics = {
                "basic_info": dao_info.get('data', {}).get('organization', {}),
                "governance_stats": {
                    "proposals": self.format_proposal_stats(proposals),
                    "token_info": token_info.get('data', {}).get('organization', {}),
                    "voting_patterns": {
                        "vote_types": vote_types,
                        "participation_trend": participation_over_time
                    }
                }
            }
            
            return analytics
        except Exception as e:
            print(f"Error aggregating DAO analytics: {e}")
            return {}

    def format_proposal_stats(self, proposal_data: Dict) -> Dict[str, Any]:
        """Formats proposal data into detailed analytics."""
        if not proposal_data or 'data' not in proposal_data:
            return {}
            
        formatted = {}
        try:
            if 'proposals' in proposal_data['data']:
                proposals = proposal_data['data']['proposals']['nodes']
                formatted['total_proposals'] = len(proposals)
                formatted['status_counts'] = {}
                formatted['vote_distribution'] = {}
                formatted['proposal_timeline'] = []
                
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
                            formatted['vote_distribution'][vote_type].append({
                                'percent': float(stat.get('percent', 0)),
                                'votes': stat.get('votesCount', 0),
                                'voters': stat.get('votersCount', 0)
                            })
                    
                    # Timeline data
                    if proposal.get('start') and proposal.get('end'):
                        formatted['proposal_timeline'].append({
                            'id': proposal.get('id'),
                            'title': proposal.get('metadata', {}).get('title'),
                            'start': proposal['start'].get('timestamp'),
                            'end': proposal['end'].get('timestamp'),
                            'status': status
                        })
                
                # Calculate averages for vote distributions
                for vote_type in formatted['vote_distribution']:
                    votes = formatted['vote_distribution'][vote_type]
                    if votes:
                        formatted['vote_distribution'][vote_type] = {
                            'average_percent': sum(v['percent'] for v in votes) / len(votes),
                            'total_votes': sum(int(v['votes']) for v in votes),
                            'total_voters': sum(v['voters'] for v in votes),
                            'occurrences': len(votes)
                        }
                    
            return formatted
            
        except Exception as e:
            print(f"Error formatting proposal stats: {e}")
            return {}

    def get_key_daos(self) -> List[str]:
        """Returns a list of key DAOs on Arbitrum and Base."""
        return [
            # Arbitrum DAOs
            "arbitrum",
            "gmx-governance", 
            "jones-dao",
            "camelot",
            "radiant",
            # Base DAOs
            "base",
            "aerodrome",
            "baseswap"
        ]