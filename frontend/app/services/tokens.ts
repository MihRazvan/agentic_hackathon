import { getPortfolios, getTokens } from '@coinbase/onchainkit/api';
import { TokenHolding } from '../types/delegations';
import { base } from 'viem/chains';

export async function getTokenHoldings(address: string): Promise<TokenHolding[]> {
    if (!address) return [];

    try {
        // Get portfolio data for the address
        const portfolioResponse = await getPortfolios({
            addresses: [address]
        });

        // Filter for tokens on Base network only
        const baseTokens = portfolioResponse.portfolios[0]?.tokens.filter(token =>
            token.chain_id === `eip155:${base.id}`
        );

        // Convert to TokenHolding format
        return baseTokens?.map(token => ({
            token_address: token.address,
            chain_id: token.chain_id,
            balance: token.raw_amount
        })) || [];

    } catch (error) {
        console.error('Error fetching token holdings:', error);
        return [];
    }
}

// Helper function to get token details by address
export async function getTokenDetails(address: string) {
    try {
        const tokens = await getTokens({
            limit: '1',
            search: address
        });
        return tokens[0];
    } catch (error) {
        console.error('Error fetching token details:', error);
        return null;
    }
}