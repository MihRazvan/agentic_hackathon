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
        console.log('Using chain ID:', `eip155:${base.id}`);

        const portfolioResponse = await getPortfolios({
            addresses: [address],
            chains: [`eip155:${base.id}`],
            includeNativeBalances: true,
            includeTokenBalances: true
        });

        console.log('Raw portfolio response:', JSON.stringify(portfolioResponse, null, 2));

        const portfolio = portfolioResponse?.portfolios?.[0];
        if (!portfolio) {
            console.log('No portfolio found');
            return [];
        }

        const holdings: TokenHolding[] = [];

        // Extract ETH balance from tokenBalances
        const ethBalance = portfolio.tokenBalances?.find(token => token.symbol === 'ETH');
        if (ethBalance?.cryptoBalance) {
            holdings.push({
                token_address: '0x0000000000000000000000000000000000000000', // ETH address
                chain_id: `eip155:${base.id}`,
                balance: ethBalance.cryptoBalance
            });
        }

        // Add other token balances (if any)
        const otherTokens = portfolio.tokenBalances?.filter(token => token.symbol !== 'ETH') || [];
        holdings.push(...otherTokens.map(token => ({
            token_address: token.address || '',
            chain_id: `eip155:${base.id}`,
            balance: token.cryptoBalance || '0'
        })));

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