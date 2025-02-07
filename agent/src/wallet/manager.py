# agent/src/wallet/manager.py
from typing import Dict, List, Any
from ..tally.client import TallyClient

class WalletManager:
    def __init__(self):
        self.tally_client = TallyClient()
    
    async def get_dao_involvement(self, wallet_address: str) -> Dict[str, Any]:
        """Get comprehensive information about user's DAO involvement."""
        try:
            # Get list of key DAOs to check
            key_daos = self.tally_client.get_key_daos()
            user_involvement = {
                "active_delegations": [],
                "potential_daos": [],
                "error": None
            }
            
            # Check each DAO for user involvement
            for dao_slug in key_daos:
                dao_data = self.tally_client.get_dao_metadata(dao_slug)
                if not dao_data or 'data' not in dao_data:
                    continue
                
                org_id = dao_data['data']['organization']['id']
                
                # Check delegation info
                delegate_info = self.tally_client.get_delegate_info(wallet_address, org_id)
                if delegate_info and 'data' in delegate_info and delegate_info['data'].get('delegate'):
                    user_involvement["active_delegations"].append({
                        "dao_slug": dao_slug,
                        "dao_name": dao_data['data']['organization']['name'],
                        "delegation_info": delegate_info['data']['delegate']
                    })
                
                # Check governance activity
                activity = self.tally_client.get_user_governance_activity(wallet_address, org_id)
                if activity and 'data' in activity and activity['data'].get('votes', {}).get('nodes'):
                    if dao_slug not in [d["dao_slug"] for d in user_involvement["active_delegations"]]:
                        user_involvement["potential_daos"].append({
                            "dao_slug": dao_slug,
                            "dao_name": dao_data['data']['organization']['name'],
                            "activity": activity['data']['votes']
                        })
            
            return user_involvement
            
        except Exception as e:
            return {
                "active_delegations": [],
                "potential_daos": [],
                "error": str(e)
            }