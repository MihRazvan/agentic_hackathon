'use client';

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
import ImageSvg from './svg/Image';

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="p-4 border-b border-[var(--card-border)]">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10">
              <ImageSvg />
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[var(--metallic-silver)] to-white">
              Tabula
            </h1>
          </div>
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
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* DAO Delegations Section */}
          <section className="glass-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Your DAO Delegations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Placeholder cards - will be replaced with real data */}
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)]">
                  <h3 className="font-medium">Example DAO {i}</h3>
                  <p className="text-sm text-gray-400">Delegated: 1,000 tokens</p>
                </div>
              ))}
            </div>
          </section>

          {/* Potential Delegations Section */}
          <section className="glass-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Recommended Delegations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Placeholder cards - will be replaced with real data */}
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)]">
                  <h3 className="font-medium">Potential DAO {i}</h3>
                  <p className="text-sm text-gray-400">Available: 500 tokens</p>
                </div>
              ))}
            </div>
          </section>

          {/* Updates and Chat Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* DAO Updates */}
            <section className="glass-card rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">DAO Updates</h2>
              <div className="space-y-4">
                {/* Placeholder updates - will be replaced with real data */}
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)]">
                    <h3 className="font-medium">Update {i}</h3>
                    <p className="text-sm text-gray-400">Lorem ipsum dolor sit amet</p>
                  </div>
                ))}
              </div>
            </section>

            {/* AI Chat */}
            <section className="glass-card rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Governance Assistant</h2>
              <div className="h-[400px] flex flex-col">
                <div className="flex-1 overflow-y-auto p-4 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)] mb-4">
                  {/* Chat messages will go here */}
                  <p className="text-gray-400">Ask me anything about DAO governance...</p>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Type your question..."
                    className="flex-1 px-4 py-2 rounded-lg bg-[var(--card-bg)] border border-[var(--card-border)]"
                  />
                  <button className="px-4 py-2 rounded-lg alchemical-gradient text-white">
                    Send
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}