export interface NotificationPreferences {
    discordWebhookUrl?: string;
    notifyOn: {
        urgent: boolean;
        important: boolean;
        fyi: boolean;
    };
}

export interface NotificationSubscription {
    address: string;
    preferences: NotificationPreferences;
}