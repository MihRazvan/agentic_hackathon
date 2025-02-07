import { DelegationsData } from '../types/delegations';

export async function getDelegations(walletAddress: string): Promise<DelegationsData> {
    try {
        const response = await fetch(`http://localhost:8000/api/delegations/${walletAddress}`);
        if (!response.ok) {
            throw new Error('Failed to fetch delegations');
        }
        return response.json();
    } catch (error) {
        console.error('Error fetching delegations:', error);
        throw error;
    }
}