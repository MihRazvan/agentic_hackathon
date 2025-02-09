import Link from 'next/link';
import { CircleUserRound } from 'lucide-react';
import { ConnectWallet } from '@coinbase/onchainkit/wallet';

export function Navigation() {
    return (
        <nav className="nav-glass fixed top-0 w-full z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="flex items-center gap-3">
                            <div className="w-8 h-8">
                                {/* Replace with your actual logo component */}
                                <div className="w-full h-full rounded-full border border-ethereal-silver/30" />
                            </div>
                            <span className="text-xl font-medium mystic-text">TABULA</span>
                        </Link>

                        <div className="hidden md:flex items-center gap-6">
                            <Link
                                href="/dashboard"
                                className="text-sm text-ethereal-silver/70 hover:text-ethereal-silver transition-colors"
                            >
                                dashboard
                            </Link>
                            <Link
                                href="/insights"
                                className="text-sm text-ethereal-silver/70 hover:text-ethereal-silver transition-colors"
                            >
                                insights
                            </Link>
                            <Link
                                href="/alchemist"
                                className="text-sm text-ethereal-silver/70 hover:text-ethereal-silver transition-colors"
                            >
                                alchemist
                            </Link>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <ConnectWallet>
                            <button className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card hover:bg-card-hover transition-all">
                                <CircleUserRound className="w-5 h-5" />
                                <span className="text-sm">Connect</span>
                            </button>
                        </ConnectWallet>
                    </div>
                </div>
            </div>
        </nav>
    );
}