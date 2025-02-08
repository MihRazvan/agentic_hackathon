import { DaoUpdate, TokenHolding } from '../types/delegations';

export async function getDaoUpdates(daoSlugs: string[], tokenHoldings?: TokenHolding[]): Promise<DaoUpdate[]> {
    try {
        // Convert token holdings to the format expected by the API
        const formattedHoldings = tokenHoldings?.reduce((acc, holding) => {
            acc[holding.token_address] = holding.balance;
            return acc;
        }, {} as Record<string, string>);

        const response = await fetch('http://localhost:8000/api/updates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dao_slugs: daoSlugs,
                token_holdings: formattedHoldings || {}
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            console.error('API Error Response:', errorData);
            throw new Error(`API error: ${response.status}`);
        }

        const updates: DaoUpdate[] = await response.json();
        return updates;
    } catch (error) {
        console.error('Error fetching DAO updates:', error);
        throw error;
    }
}