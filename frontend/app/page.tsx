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
import { getTokenHoldings } from './services/tokens';
import type { DelegationResponse, DelegationsData } from './types/delegations';
import ImageSvg from './svg/Image';

export default function App() {
  const [delegationsData, setDelegationsData] = useState<DelegationsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectedAddress, setConnectedAddress] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDelegations() {
      if (!connectedAddress) return;

      try {
        setLoading(true);
        setError(null);

        // Get token holdings for Base network only
        const holdings = await getTokenHoldings(connectedAddress);
        console.log('Token holdings:', holdings);

        // Call your backend API
        const response = await fetch(`http://localhost:8000/api/delegations/${connectedAddress}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token_holdings: holdings }),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        setDelegationsData({
          active_delegations: data.active_delegations || [],
          available_delegations: data.available_delegations || [],
          recommended_delegations: data.recommended_delegations?.slice(0, 3) || []
        });
      } catch (err) {
        console.error(err);
        setError('Failed to fetch delegations data');
      } finally {
        setLoading(false);
      }
    }

    fetchDelegations();
  }, [connectedAddress]);

  const renderDaoCard = (delegation: DelegationResponse) => (
    <div className="p-4 rounded-lg border border-[var(--card-border)] bg-[var(--card-bg)] hover:border-[var(--metallic-silver)] transition-colors">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-medium">{delegation.dao_name}</h3>
      </div>
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
  );

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
            <ConnectWallet onConnect={(address) => setConnectedAddress(address)}>
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
              <WalletDropdownDisconnect onDisconnect={() => setConnectedAddress(null)} />
            </WalletDropdown>
          </Wallet>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          {!connectedAddress ? (
            <div className="glass-card rounded-lg p-8 text-center">
              <h2 className="text-xl font-semibold mb-4">Connect Your Wallet</h2>
              <p className="text-gray-400 mb-6">Connect your wallet to view your DAO delegations and recommendations</p>
            </div>
          ) : loading ? (
            <div className="glass-card rounded-lg p-8 text-center">
              <p className="text-gray-400">Loading your DAO data...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500 text-red-500">
              {error}
            </div>
          ) : (
            <>
              {/* Active Delegations Section */}
              <section className="glass-card rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Your Active Delegations</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {delegationsData?.active_delegations.length ? (
                    delegationsData.active_delegations.map((delegation, i) => (
                      <div key={`${delegation.dao_slug}-${i}`}>
                        {renderDaoCard(delegation)}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-gray-400">
                      You haven't delegated to any DAOs yet
                    </div>
                  )}
                </div>
              </section>

              {/* Available Delegations Section */}
              <section className="glass-card rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Available Delegations</h2>
                <p className="text-gray-400 mb-4">DAOs where you hold tokens and can delegate your voting power</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {delegationsData?.available_delegations?.length ? (
                    delegationsData.available_delegations.map((delegation, i) => (
                      <div key={`${delegation.dao_slug}-${i}`}>
                        {renderDaoCard(delegation)}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-gray-400">
                      No DAOs found where you can delegate
                    </div>
                  )}
                </div>
              </section>

              {/* Recommended DAOs Section */}
              <section className="glass-card rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Discover More DAOs</h2>
                <p className="text-gray-400 mb-4">Explore these DAOs based on governance activity and community engagement</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {delegationsData?.recommended_delegations?.length ? (
                    delegationsData.recommended_delegations.map((delegation, i) => (
                      <div key={`${delegation.dao_slug}-${i}`}>
                        {renderDaoCard(delegation)}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-gray-400">
                      No recommendations available
                    </div>
                  )}
                </div>
              </section>
            </>
          )}
        </div>
      </main>
    </div>
  );
}