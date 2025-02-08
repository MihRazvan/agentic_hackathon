import { DaoUpdate } from '../types/delegations';
import { formatDistanceToNow } from 'date-fns';
import { AlertTriangle, TrendingUp, ChevronRight, ArrowUpRight } from 'lucide-react';

interface UpdateCardProps {
    update: DaoUpdate;
}

const priorityStyles = {
    urgent: 'bg-red-500/10 border-red-500/20 text-red-400',
    important: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
    fyi: 'bg-blue-500/10 border-blue-500/20 text-blue-400'
};

const categoryIcons = {
    proposal: TrendingUp,
    treasury: AlertTriangle,
    governance: ChevronRight,
    social: TrendingUp
};

export function UpdateCard({ update }: UpdateCardProps) {
    const Icon = categoryIcons[update.category];

    return (
        <div className={`p-4 rounded-lg border ${priorityStyles[update.priority]} hover:border-opacity-50 transition-colors`}>
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{update.dao_name}</span>
                </div>
                <span className="text-sm opacity-70">
                    {formatDistanceToNow(new Date(update.timestamp), { addSuffix: true })}
                </span>
            </div>

            <h3 className="font-semibold mb-2">{update.title}</h3>
            <p className="text-sm opacity-80 mb-4">{update.description}</p>

            {/* Impact Analysis */}
            {update.metadata.impact_analysis && (
                <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                        {update.metadata.impact_analysis.affected_areas.map((area) => (
                            <span key={area} className="text-xs px-2 py-1 rounded-full bg-white/5">
                                {area}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Social Sentiment */}
            {update.metadata.social_sentiment && (
                <div className="text-sm mb-4">
                    <div className="flex flex-wrap gap-2">
                        {update.metadata.social_sentiment.trending_keywords.slice(0, 3).map((keyword) => (
                            <span key={keyword} className="text-xs px-2 py-1 rounded-full bg-white/5">
                                #{keyword}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Actions */}
            {update.actions && update.actions.length > 0 && (
                <div className="flex gap-2 mt-4">
                    {update.actions.map((action) => (
                        <a
                            key={action.label}
                            href={action.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                        >
                            {action.label}
                            <ArrowUpRight className="w-4 h-4" />
                        </a>
                    ))}
                </div>
            )}
        </div>
    );
}