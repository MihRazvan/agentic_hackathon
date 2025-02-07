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