
from typing import Dict, List, Any
from ..tally.client import TallyClient

class WalletManager:
    def __init__(self):
        self.tally_client = TallyClient()
        self.supported_networks = self._get_supported_networks()
    
    def _is_significant_dao(self, dao: Dict) -> bool:
        """Filter for significant mainnet DAOs."""
        # Skip test/mock/inactive DAOs
        skip_keywords = ['test', 'mock', 'demo', 'fork', 'club']
        if any(keyword in dao.get('name', '').lower() for keyword in skip_keywords):
            return False
        
        # Major DAOs - always include
        if dao.get('slug') in self.tally_client.major_daos:
            return True
        
        # Either significant delegates or proposals
        has_significant_delegates = dao.get('delegates_count', 0) >= 50
        has_significant_proposals = dao.get('proposals_count', 0) >= 10
        
        return has_significant_delegates or has_significant_proposals
    
    def _get_supported_networks(self) -> Dict[str, Dict[str, str]]:
        """Get a list of significant DAOs and their IDs."""
        try:
            # Get all organizations
            query_result = self.tally_client.get_organizations()
            if not query_result or 'data' not in query_result:
                return {}
                
            organizations = query_result['data'].get('organizations', {}).get('nodes', [])
            networks = {}
            
            for org in organizations:
                if org.get('slug') and org.get('id'):
                    if self._is_significant_dao(org):
                        networks[org['slug']] = {
                            'id': org['id'],
                            'name': org['name'],
                            'chain_ids': org.get('chainIds', []),
                            'delegates_count': org.get('delegatesCount', 0),
                            'proposals_count': org.get('proposalsCount', 0),
                            'has_active_proposals': org.get('hasActiveProposals', False)
                        }
            
            print("\nSignificant DAOs:")
            for slug, data in networks.items():
                print(f"- {data['name']} (slug: {slug}, id: {data['id']})")
                print(f"  Chains: {', '.join(data['chain_ids'])}")
                print(f"  Delegates: {data['delegates_count']}")
                print(f"  Proposals: {data['proposals_count']}")
                print(f"  Active Proposals: {data['has_active_proposals']}")
                
            return networks
            
        except Exception as e:
            print(f"Error getting organizations: {str(e)}")
            return {}
            
    def filter_supported_networks(self, chain_id: str = None) -> Dict[str, Dict[str, str]]:
        """Filter networks based on chain ID."""
        filtered = {}
        for slug, data in self.supported_networks.items():
            # If chain_id is specified, only include DAOs on that chain
            if chain_id and chain_id not in data['chain_ids']:
                continue
            filtered[slug] = data
            
        return filtered
    
    def _process_delegation_info(self, delegate_info: Dict) -> Dict:
        """Process and clean delegation information."""
        if not delegate_info or 'data' not in delegate_info or not delegate_info.get('delegate'):
            return None
            
        delegate = delegate_info['data']['delegate']
        return {
            "dao_name": delegate['organization']['name'],
            "votes_count": delegate['votesCount'],
            "delegators_count": delegate['delegatorsCount'],
            "user_info": {
                "address": delegate['account']['address'],
                "name": delegate['account'].get('name'),
                "ens": delegate['account'].get('ens')
            },
            "token": {
                "name": delegate['token']['name'],
                "symbol": delegate['token']['symbol']
            },
            "proposals_count": delegate['organization']['proposalsCount']
        }
        
    def filter_supported_networks(self, chain_id: str = None) -> Dict[str, Dict[str, str]]:
        """Filter networks based on chain ID and other criteria."""
        filtered = {}
        for slug, data in self.supported_networks.items():
            # If chain_id is specified, only include DAOs on that chain
            if chain_id and chain_id not in data['chain_ids']:
                continue
                
            # Additional filters can be added here
            filtered[slug] = data
            
        return filtered
    
    async def get_dao_involvement(self, wallet_address: str) -> Dict[str, Any]:
        """Get comprehensive information about user's DAO involvement."""
        try:
            involvement = {
                "active_delegations": [],
                "potential_daos": [],
                "user_info": {
                    "address": wallet_address,
                    "ens": None,
                    "name": None
                },
                "error": None
            }
            
            # Get networks
            networks = self.filter_supported_networks()
            
            if not networks:
                involvement["error"] = "No supported DAOs found"
                return involvement
            
            # Check each supported DAO
            for dao_slug, dao_info in networks.items():
                try:
                    # Get delegation info
                    delegate_info = self.tally_client.get_delegate_info(wallet_address, dao_info['id'])
                    processed_info = self._process_delegation_info(delegate_info)
                    
                    # Get token balance for this DAO
                    balance_info = await self._check_token_balance(wallet_address, dao_info)
                    has_tokens = balance_info and balance_info.get('balance', 0) > 0
                    
                    if processed_info:
                        # User has active delegation
                        involvement["active_delegations"].append({
                            "dao_slug": dao_slug,
                            "dao_name": dao_info['name'],
                            "chain_ids": dao_info['chain_ids'],
                            "has_active_proposals": dao_info['has_active_proposals'],
                            **processed_info
                        })
                    elif has_tokens:
                        # User has tokens but no delegation
                        involvement["potential_daos"].append({
                            "dao_slug": dao_slug,
                            "dao_name": dao_info['name'],
                            "chain_ids": dao_info['chain_ids'],
                            "delegates_count": dao_info['delegates_count'],
                            "proposals_count": dao_info['proposals_count'],
                            "has_active_proposals": dao_info['has_active_proposals'],
                            "token_balance": balance_info['balance'],
                            "token_symbol": balance_info['symbol']
                        })
                    
                except Exception as e:
                    print(f"Error processing {dao_info['name']}: {str(e)}")
                    continue
            
            return involvement
            
        except Exception as e:
            return {
                "active_delegations": [],
                "potential_daos": [],
                "user_info": {"address": wallet_address},
                "error": str(e)
            }

    async def _check_token_balance(self, wallet_address: str, dao_info: Dict) -> Dict:
        """Check token balance for a specific DAO."""
        try:
            # Get token info from DAO
            token_id = dao_info.get('token_id')
            if not token_id:
                return None
                
            # Use TallyClient to get token balance
            balance = self.tally_client.get_token_balance(wallet_address, token_id)
            
            if balance:
                return {
                    'balance': balance.get('balance', 0),
                    'symbol': balance.get('symbol', 'UNKNOWN')
                }
                
        except Exception as e:
            print(f"Error checking token balance: {str(e)}")
            return None
            
        return None

    async def get_specific_dao_info(self, dao_slug: str) -> Dict[str, Any]:
        """Get detailed information about a specific DAO."""
        try:
            if dao_slug not in self.supported_networks:
                return {"error": f"DAO {dao_slug} not found"}
                
            dao_info = self.supported_networks[dao_slug]
            
            # Get additional DAO data if needed
            metadata = self.tally_client.get_dao_metadata(dao_slug)
            active_proposals = self.tally_client.get_active_proposals(dao_info['id'])
            
            return {
                "basic_info": dao_info,
                "metadata": metadata.get('data', {}).get('organization', {}),
                "active_proposals": active_proposals.get('data', {}).get('proposals', {}).get('nodes', [])
            }
            
        except Exception as e:
            return {"error": str(e)}