// app/services/delegations.ts

import { DelegationsData } from '../types/delegations';

export async function getDelegations(walletAddress?: string): Promise<DelegationsData> {
    console.log('getDelegations called with address:', walletAddress);

    if (!walletAddress) {
        throw new Error('Wallet address is required');
    }

    try {
        console.log('Fetching from:', `http://localhost:8000/api/delegations/${walletAddress}`);
        const response = await fetch(`http://localhost:8000/api/delegations/${walletAddress}`);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', response.status, errorText);
            throw new Error(`Failed to fetch delegations: ${response.status} ${errorText}`);
        }

        const data = await response.json();
        console.log('API Response:', data);

        // Transform the data to match our frontend structure
        const transformedData = {
            active_delegations: data.active_delegations || [],
            potential_daos: data.potential_daos || [],
            recommended_delegations: data.recommended_delegations || []
        };

        console.log('Transformed data:', transformedData);
        return transformedData;
    } catch (error) {
        console.error('Error in getDelegations:', error);
        throw error;
    }
}