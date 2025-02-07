from typing import Dict, List, Any
from ..tally.client import TallyClient

class WalletManager:
    def __init__(self):
        self.tally_client = TallyClient()
        self.supported_networks = self._get_supported_networks()
    
    def _get_supported_networks(self) -> Dict[str, Dict[str, str]]:
        """Get a list of all available DAOs and their IDs."""
        try:
            # Get all organizations
            query_result = self.tally_client.get_organizations()
            if not query_result or 'data' not in query_result:
                return {}
                
            organizations = query_result['data'].get('organizations', {}).get('nodes', [])
            networks = {}
            
            for org in organizations:
                if org.get('slug') and org.get('id'):
                    networks[org['slug']] = {
                        'id': org['id'],
                        'name': org['name'],
                        'chain_ids': org.get('chainIds', []),
                        'delegates_count': org.get('delegatesCount', 0),
                        'proposals_count': org.get('proposalsCount', 0),
                        'has_active_proposals': org.get('hasActiveProposals', False)
                    }
            
            print("\nAvailable DAOs:")
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
    
    async def get_dao_involvement(self, wallet_address: str, chain_id: str = None) -> Dict[str, Any]:
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
            
            # Get networks filtered by chain if specified
            networks = self.filter_supported_networks(chain_id)
            
            # If no networks found, return early
            if not networks:
                involvement["error"] = f"No supported DAOs found{' for chain ' + chain_id if chain_id else ''}"
                return involvement
            
            # Check each supported DAO
            for dao_slug, dao_info in networks.items():
                try:
                    # Get delegation info using the numeric org ID
                    delegate_info = self.tally_client.get_delegate_info(wallet_address, dao_info['id'])
                    processed_info = self._process_delegation_info(delegate_info)
                    
                    if processed_info:
                        # Update user info if available
                        if not involvement["user_info"]["name"]:
                            involvement["user_info"].update({
                                "name": processed_info["user_info"]["name"],
                                "ens": processed_info["user_info"]["ens"]
                            })
                        
                        involvement["active_delegations"].append({
                            "dao_slug": dao_slug,
                            "dao_name": dao_info['name'],
                            "chain_ids": dao_info['chain_ids'],
                            "has_active_proposals": dao_info['has_active_proposals'],
                            **processed_info
                        })
                    else:
                        # Add to potential DAOs if no active delegation
                        involvement["potential_daos"].append({
                            "dao_slug": dao_slug,
                            "dao_name": dao_info['name'],
                            "chain_ids": dao_info['chain_ids'],
                            "delegates_count": dao_info['delegates_count'],
                            "proposals_count": dao_info['proposals_count'],
                            "has_active_proposals": dao_info['has_active_proposals']
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