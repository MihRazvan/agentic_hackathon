import { NotificationPreferences } from '../types/notifications';

export async function subscribeToNotifications(
    address: string,
    preferences: NotificationPreferences
): Promise<boolean> {
    try {
        const response = await fetch('http://localhost:8000/api/notifications/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                address,
                preferences,
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to subscribe to notifications');
        }

        return true;
    } catch (error) {
        console.error('Error subscribing to notifications:', error);
        throw error;
    }
}

export async function unsubscribeFromNotifications(address: string): Promise<boolean> {
    try {
        const response = await fetch(`http://localhost:8000/api/notifications/unsubscribe/${address}`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error('Failed to unsubscribe from notifications');
        }

        return true;
    } catch (error) {
        console.error('Error unsubscribing from notifications:', error);
        throw error;
    }
}