'use client';

import { useEffect, useState } from 'react';
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
import { useAccount } from 'wagmi';
import ImageSvg from './svg/Image';
import { getDelegations } from './services/delegations';
import type { DelegationsData } from './types/delegations';

export default function App() {
  const { address } = useAccount();
  const [delegationsData, setDelegationsData] = useState<DelegationsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use the provided test address
  const testAddress = '0x746bb7beFD31D9052BB8EbA7D5dD74C9aCf54C6d';
  const activeAddress = address || testAddress;

  useEffect(() => {
    async function fetchDelegations() {
      try {
        setLoading(true);
        setError(null);
        const data = await getDelegations(activeAddress);
        setDelegationsData(data);
      } catch (err) {
        setError('Failed to fetch delegations data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (activeAddress) {
      fetchDelegations();
    }
  }, [activeAddress]);

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
          {error && (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500 text-red-500">
              {error}
            </div>
          )}

          {/* DAO Delegations Section */}
          <section className="glass-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Your DAO Delegations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {loading ? (
                <div className="col-span-full text-center py-8 text-gray-400">
                  Loading delegations...
                </div>
              ) : delegationsData?.active_delegations.map((delegation, i) => (
                <div key={i} className="p-4 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)]">
                  <h3 className="font-medium">{delegation.dao_name}</h3>
                  <p className="text-sm text-gray-400">{delegation.token_amount}</p>
                  {delegation.has_active_proposals && (
                    <div className="mt-2 text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400 inline-block">
                      Active Proposals
                    </div>
                  )}
                  {delegation.proposals_count !== undefined && (
                    <p className="text-sm text-gray-400 mt-2">
                      {delegation.proposals_count} total proposals
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Potential Delegations Section */}
          <section className="glass-card rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Recommended Delegations</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {loading ? (
                <div className="col-span-full text-center py-8 text-gray-400">
                  Loading recommendations...
                </div>
              ) : delegationsData?.recommended_delegations.map((delegation, i) => (
                <div key={i} className="p-4 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)]">
                  <h3 className="font-medium">{delegation.dao_name}</h3>
                  <p className="text-sm text-gray-400">{delegation.token_amount}</p>
                  {delegation.has_active_proposals && (
                    <div className="mt-2 text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400 inline-block">
                      Active Proposals
                    </div>
                  )}
                  {delegation.proposals_count !== undefined && (
                    <p className="text-sm text-gray-400 mt-2">
                      {delegation.proposals_count} total proposals
                    </p>
                  )}
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
                {/* We'll integrate this with real updates later */}
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