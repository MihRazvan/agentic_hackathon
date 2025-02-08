import { DaoUpdate } from '../types/delegations';
import { formatDistanceToNow } from 'date-fns';
import { AlertTriangle, TrendingUp, ChevronRight, ArrowUpRight, LineChart, Wallet, Users } from 'lucide-react';

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
    treasury: Wallet,
    governance: Users,
    social: LineChart
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
                    {update.metadata.impact_analysis.risk_level && (
                        <div className="mt-2">
                            <span className={`text-xs px-2 py-1 rounded-full ${update.metadata.impact_analysis.risk_level === 'high' ? 'bg-red-500/20 text-red-400' :
                                    update.metadata.impact_analysis.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                        'bg-green-500/20 text-green-400'
                                }`}>
                                {update.metadata.impact_analysis.risk_level.toUpperCase()} RISK
                            </span>
                        </div>
                    )}
                </div>
            )}

            {/* Vote Stats */}
            {update.metadata.vote_stats && update.metadata.vote_stats.length > 0 && (
                <div className="mb-4 p-3 rounded-lg bg-white/5">
                    <div className="grid grid-cols-2 gap-4">
                        {update.metadata.vote_stats.map((stat: any) => (
                            <div key={stat.type} className="text-center">
                                <div className="text-sm opacity-70">{stat.type.toUpperCase()}</div>
                                <div className="font-semibold">{stat.votesCount}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Treasury Details */}
            {update.category === 'treasury' && update.metadata.treasury_size && (
                <div className="mb-4 p-3 rounded-lg bg-white/5">
                    <div className="text-sm opacity-70">Treasury Size</div>
                    <div className="font-semibold">{update.metadata.treasury_size}</div>
                </div>
            )}

            {/* Social Sentiment */}
            {update.metadata.social_sentiment && (
                <div className="text-sm mb-4">
                    <div className="flex items-center gap-2 mb-2">
                        <div className="text-xs opacity-70">Sentiment Score</div>
                        <div className={`px-2 py-0.5 rounded-full text-xs ${update.metadata.social_sentiment.score > 0.5 ? 'bg-green-500/20 text-green-400' :
                                update.metadata.social_sentiment.score < 0 ? 'bg-red-500/20 text-red-400' :
                                    'bg-yellow-500/20 text-yellow-400'
                            }`}>
                            {(update.metadata.social_sentiment.score * 100).toFixed(0)}%
                        </div>
                    </div>
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