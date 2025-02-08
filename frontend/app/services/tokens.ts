import { getPortfolios } from '@coinbase/onchainkit/api';
import { TokenHolding } from '../types/delegations';
import { base } from 'viem/chains';

export async function getTokenHoldings(address: string): Promise<TokenHolding[]> {
    if (!address) {
        console.log('No address provided to getTokenHoldings');
        return [];
    }

    try {
        console.log('Fetching portfolio data for address:', address);
        console.log('Using chain ID:', `eip155:${base.id}`); // Log the chain ID we're using

        // Get portfolio data for the address
        const portfolioResponse = await getPortfolios({
            addresses: [address],
            chains: [`eip155:${base.id}`], // Base network
            includeNativeBalances: true, // Add this to include ETH balance
            includeTokenBalances: true    // Add this to explicitly request token balances
        });

        console.log('Raw portfolio response:', JSON.stringify(portfolioResponse, null, 2));

        // Safely access the portfolio data
        const portfolio = portfolioResponse?.portfolios?.[0];
        if (!portfolio) {
            console.log('No portfolio found');
            return [];
        }

        const holdings: TokenHolding[] = [];

        // Add native ETH balance if present
        if (portfolio.native_balance) {
            holdings.push({
                token_address: '0x0000000000000000000000000000000000000000', // ETH address
                chain_id: `eip155:${base.id}`,
                balance: portfolio.native_balance.raw_amount || '0'
            });
        }

        // Add other token balances
        if (portfolio.tokens?.length) {
            holdings.push(...portfolio.tokens.map(token => ({
                token_address: token.address,
                chain_id: `eip155:${base.id}`,
                balance: token.raw_amount || '0'
            })));
        }

        console.log('Final token holdings:', holdings);
        return holdings;

    } catch (error) {
        console.error('Error fetching token holdings:', error);
        if (error instanceof Error) {
            console.error('Error name:', error.name);
            console.error('Error message:', error.message);
            console.error('Error stack:', error.stack);
        }
        return [];
    }
}