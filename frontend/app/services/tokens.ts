import { TokenHolding } from '../types/delegations';
import { readContract } from '@wagmi/core';
import { erc20Abi } from 'viem';

// Known governance tokens
const GOVERNANCE_TOKENS = {
    'eip155:42161': [ // Arbitrum
        '0x912CE59144191C1204E64559FE8253a0e49E6548', // ARB
    ],
    'eip155:8453': [ // Base
        '0x1C7a460413dD4e964f96D8dFC56E7223cE88CD85', // Seamless
        '0x968D6A288d7B024D5012c0B25d67A889E4E3eC19', // Internet Computer
        '0xbb5D04c40Fa063FAF213c4E0B8086655164269Ef', // Gloom
    ]
};

export async function getTokenHoldings(address: string): Promise<TokenHolding[]> {
    if (!address) return [];

    const holdings: TokenHolding[] = [];

    for (const [chainId, tokens] of Object.entries(GOVERNANCE_TOKENS)) {
        for (const tokenAddress of tokens) {
            try {
                const balance = await readContract({
                    address: tokenAddress as `0x${string}`,
                    abi: erc20Abi,
                    functionName: 'balanceOf',
                    args: [address as `0x${string}`],
                    chainId: parseInt(chainId.split(':')[1])
                });

                if (balance > 0n) {
                    holdings.push({
                        token_address: tokenAddress,
                        chain_id: chainId,
                        balance: balance.toString()
                    });
                }
            } catch (error) {
                console.error(`Error fetching balance for token ${tokenAddress} on chain ${chainId}:`, error);
            }
        }
    }

    return holdings;
}