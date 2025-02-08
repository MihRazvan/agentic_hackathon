export interface DelegationResponse {
    dao_name: string;
    dao_slug: string;
    token_amount: string;
    chain_ids: string[];
    votes_count?: string;
    proposals_count?: number;
    has_active_proposals?: boolean;
}

export interface DelegationsData {
    active_delegations: DelegationResponse[];
    potential_daos: DelegationResponse[];
    recommended_delegations: DelegationResponse[];
}

const CHAIN_ID_MAP: Record<string, string> = {
    'eip155:42161': 'arbitrum',
    'eip155:8453': 'base'
};

export const CHAIN_LOGOS: Record<string, string> = {
    'arbitrum': '/chain-logos/arbitrum.svg',
    'base': '/chain-logos/base.svg'
};

export function getChainLogo(chainId: string): string | undefined {
    const chainName = CHAIN_ID_MAP[chainId];
    return chainName ? CHAIN_LOGOS[chainName] : undefined;
}