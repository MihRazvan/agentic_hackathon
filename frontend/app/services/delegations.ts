import { DelegationsData, TokenHolding } from '../types/delegations';

export async function getDelegations(walletAddress?: string, tokenHoldings?: TokenHolding[]): Promise<DelegationsData> {
    console.log('getDelegations called with address:', walletAddress);
    console.log('Token holdings:', tokenHoldings);

    if (!walletAddress) {
        throw new Error('Wallet address is required');
    }

    try {
        const response = await fetch(`http://localhost:8000/api/delegations/${walletAddress}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token_holdings: tokenHoldings || [] }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', response.status, errorText);
            throw new Error(`Failed to fetch delegations: ${response.status} ${errorText}`);
        }

        const data = await response.json();
        console.log('API Response:', data);

        return {
            active_delegations: data.active_delegations || [],
            available_delegations: data.available_delegations || [],
            recommended_delegations: data.recommended_delegations || []
        };
    } catch (error) {
        console.error('Error in getDelegations:', error);
        throw error;
    }
}