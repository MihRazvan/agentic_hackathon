# agent/src/wallet/tests/test_manager.py
import pytest
from ...wallet.manager import WalletManager

@pytest.mark.asyncio
async def test_get_user_daos():
    manager = WalletManager()
    # Test wallet address with known delegations
    test_address = "0x8c595DA827F4182bC0E3917BccA8e654DF8223E1"
    
    result = await manager.get_user_daos(test_address)
    assert result is not None
    assert "active_delegations" in result
    assert "error" not in result or result["error"] is None