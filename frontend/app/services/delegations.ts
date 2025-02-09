export interface TokenHolding {
    token_address: string;
    chain_id: string;
    balance: string;
}

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
    available_delegations: DelegationResponse[];
    recommended_delegations: DelegationResponse[];
}

export type UpdatePriority = 'urgent' | 'important' | 'fyi';
export type UpdateCategory = 'proposal' | 'treasury' | 'governance' | 'social';

export interface UpdateAction {
    type: 'link' | 'vote' | 'delegate';
    label: string;
    url: string;
}

export interface DaoUpdate {
    id: string;
    dao_slug: string;
    dao_name: string;
    title: string;
    description: string;
    priority: UpdatePriority;
    category: UpdateCategory;
    timestamp: string;
    metadata: {
        proposal_id?: string;
        proposal_title?: string;
        impact_analysis?: {
            summary: string;
            affected_areas: string[];
            risk_level?: 'low' | 'medium' | 'high';
        };
        treasury_change?: {
            amount: string;
            token_symbol: string;
            direction: 'inflow' | 'outflow';
        };
        social_sentiment?: {
            score: number;
            trending_keywords: string[];
            total_mentions: number;
        };
    };
    actions?: UpdateAction[];
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