import { useState } from 'react';
import { Bell, BellOff, Settings } from 'lucide-react';
import { NotificationPreferences } from '../types/notifications';
import { subscribeToNotifications, unsubscribeFromNotifications } from '../services/notifications';

interface NotificationSettingsProps {
    address: string;
}

export function NotificationSettings({ address }: NotificationSettingsProps) {
    const [isSubscribed, setIsSubscribed] = useState(false);
    const [webhookUrl, setWebhookUrl] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [preferences, setPreferences] = useState<NotificationPreferences>({
        notifyOn: {
            urgent: true,
            important: true,
            fyi: false
        }
    });

    const handleSubscribe = async () => {
        try {
            if (!webhookUrl) {
                alert('Please enter a Discord webhook URL');
                return;
            }

            await subscribeToNotifications(address, {
                ...preferences,
                discordWebhookUrl: webhookUrl
            });

            setIsSubscribed(true);
            setShowForm(false);
        } catch (error) {
            console.error('Error subscribing to notifications:', error);
            alert('Failed to subscribe to notifications');
        }
    };

    const handleUnsubscribe = async () => {
        try {
            await unsubscribeFromNotifications(address);
            setIsSubscribed(false);
            setWebhookUrl('');
        } catch (error) {
            console.error('Error unsubscribing from notifications:', error);
            alert('Failed to unsubscribe from notifications');
        }
    };

    return (
        <div className="relative" >
            <button
                onClick={() => isSubscribed ? handleUnsubscribe() : setShowForm(!showForm)}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2"
                title={isSubscribed ? 'Manage notifications' : 'Enable notifications'}
            >
                {
                    isSubscribed ? (
                        <>
                            <Bell className="w-5 h-5 text-ethereal-silver" />
                            <span className="text-sm text-ethereal-silver/70" > Notifications On </span>
                        </>
                    ) : (
                        <>
                            <BellOff className="w-5 h-5 text-ethereal-silver/70" />
                            <span className="text-sm text-ethereal-silver/70" > Enable Notifications </span>
                        </>
                    )
                }
            </button>

            {
                showForm && !isSubscribed && (
                    <div className="absolute right-0 top-12 w-80 glass-card p-4 rounded-lg z-50 border border-white/10" >
                        <div className="space-y-4" >
                            <div>
                                <label className="block text-sm mb-2 text-ethereal-silver/70" > Discord Webhook URL </label>
                                < input
                                    type="text"
                                    value={webhookUrl}
                                    onChange={(e) => setWebhookUrl(e.target.value)
                                    }
                                    placeholder="https://discord.com/api/webhooks/..."
                                    className="w-full p-2 rounded-lg bg-white/10 border border-white/20 text-ethereal-silver placeholder-ethereal-silver/30"
                                />
                            </div>

                            < div className="space-y-2" >
                                <label className="block text-sm mb-2 text-ethereal-silver/70" > Notify me about: </label>
                                {
                                    Object.entries(preferences.notifyOn).map(([key, value]) => (
                                        <label key={key} className="flex items-center gap-2 text-ethereal-silver/70" >
                                            <input
                                                type="checkbox"
                                                checked={value}
                                                onChange={(e) => setPreferences(prev => ({
                                                    ...prev,
                                                    notifyOn: {
                                                        ...prev.notifyOn,
                                                        [key]: e.target.checked
                                                    }
                                                }))}
                                                className="rounded bg-white/10 border-white/20"
                                            />
                                            <span className="capitalize" > {key} updates </span>
                                        </label>
                                    ))}
                            </div>

                            < div className="flex justify-end gap-2" >
                                <button
                                    onClick={() => setShowForm(false)}
                                    className="px-4 py-2 rounded-lg hover:bg-white/10 text-ethereal-silver/70"
                                >
                                    Cancel
                                </button>
                                < button
                                    onClick={handleSubscribe}
                                    className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-ethereal-silver"
                                >
                                    Subscribe
                                </button>
                            </div>
                        </div>
                    </div>
                )}
        </div>
    );
}