import Link from 'next/link';
import Image from 'next/image';
import {
    ConnectWallet,
    Wallet,
    WalletDropdown,
    WalletDropdownLink,
    WalletDropdownDisconnect,
} from '@coinbase/onchainkit/wallet';
import {
    Address,
    Avatar,
    Name,
    Identity,
    EthBalance,
} from '@coinbase/onchainkit/identity';

export function Navigation() {
    return (
        <nav className="nav-glass fixed top-0 w-full z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="flex items-center gap-3">
                            <Image
                                src="/logo WhiteOnTransparent.png"
                                alt="Tabula"
                                width={120}
                                height={40}
                                className="tabula-logo"
                            />
                        </Link>

                        <div className="hidden md:flex items-center gap-6">
                            <Link
                                href="/dashboard"
                                className="text-sm text-ethereal-silver/70 hover:text-ethereal-silver transition-colors flex items-center gap-2"
                            >
                                <Image
                                    src="/icon WhiteOnTransparent.png"
                                    alt=""
                                    width={24}
                                    height={24}
                                    className="nav-icon"
                                />
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
                                className="text-sm text-ethereal-silver/70 hover:text-ethereal-silver transition-colors flex items-center gap-2"
                            >
                                <Image
                                    src="/small icon alchemist.png"
                                    alt=""
                                    width={24}
                                    height={24}
                                    className="nav-icon"
                                />
                                alchemist
                            </Link>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <Wallet>
                            <ConnectWallet>
                                <Avatar className="h-6 w-6" />
                                <Name />
                            </ConnectWallet>
                            <WalletDropdown>
                                <Identity className="px-4 pt-3 pb-2" hasCopyAddressOnClick>
                                    <Avatar />
                                    <Name />
                                    <Address />
                                    <EthBalance />
                                </Identity>
                                <WalletDropdownLink
                                    icon="wallet"
                                    href="https://keys.coinbase.com"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Wallet
                                </WalletDropdownLink>
                                <WalletDropdownDisconnect />
                            </WalletDropdown>
                        </Wallet>
                    </div>
                </div>
            </div>
        </nav>
    );
}