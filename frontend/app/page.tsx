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
import { getTokenHoldings } from './services/tokens';
import { getDelegations } from './services/delegations';
import { getDaoUpdates } from './services/updates';
import { UpdateCard } from './components/UpdateCard';
import { NotificationSettings } from './components/NotificationSettings';
import type { DelegationResponse, DelegationsData, DaoUpdate } from './types/delegations';
import Image from 'next/image';

export default function App() {
  const { address } = useAccount();
  const [delegationsData, setDelegationsData] = useState<DelegationsData | null>(null);
  const [updates, setUpdates] = useState<DaoUpdate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      if (!address) {
        setDelegationsData(null);
        setUpdates([]);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const holdings = await getTokenHoldings(address);
        const data = await getDelegations(address, holdings);
        setDelegationsData(data);

        const daoSlugs = [
          ...data.active_delegations.map(d => d.dao_slug),
          ...data.available_delegations.map(d => d.dao_slug)
        ];

        if (daoSlugs.length > 0) {
          const updatesData = await getDaoUpdates(daoSlugs, holdings);
          setUpdates(updatesData);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch data');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [address]);

  const renderDaoCard = (delegation: DelegationResponse) => {
    return (
      <div className="glass-card p-4 rounded-lg">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-medium mystic-text">{delegation.dao_name}</h3>
        </div>
        <p className="text-sm text-ethereal-silver/70">{delegation.token_amount}</p>
        {delegation.has_active_proposals && (
          <div className="mt-2 text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400 inline-block">
            Active Proposals
          </div>
        )}
      </div>
    );
  };

  if (!address) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-deep-blue">
        <div className="text-center max-w-xl mx-auto flex flex-col items-center">
          <div className="mb-24">
            <Image
              src="/big icon alchemist.png"
              alt="Alchemist"
              width={200}
              height={200}
              priority
              className="mx-auto"
            />
          </div>
          <div className="mb-8">
            <Image
              src="/logo WhiteOnTransparent.png"
              alt="Tabula"
              width={500}
              height={150}
              priority
              className="mx-auto"
            />
          </div>
          <p className="text-2xl text-ethereal-silver/80 mb-24">
            transmute data into decisions
          </p>
          <button className="px-12 py-3 glass-card rounded-lg hover:bg-card-hover transition-all text-lg">
            Connect Wallet
          </button>
        </div>
      </div>
    );
  }

  const urgentUpdates = updates.filter(u => u.priority === 'urgent');
  const importantUpdates = updates.filter(u => u.priority === 'important');
  const fyiUpdates = updates.filter(u => u.priority === 'fyi');

  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 pt-20 p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          {loading ? (
            <div className="glass-card rounded-lg p-8 text-center">
              <p className="text-ethereal-silver/70">Loading your DAO data...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500 text-red-500">
              {error}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <section className="glass-card rounded-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold mystic-text">The Ledger of Omens</h2>
                    {address && (
                      <div className="flex items-center gap-2">
                        <NotificationSettings address={address} />
                      </div>
                    )}
                  </div>
                  <div className="h-[600px] overflow-y-auto pr-2 space-y-4 scrollbar-thin">
                    {updates.length > 0 ? (
                      <>
                        {urgentUpdates.length > 0 && (
                          <div className="space-y-2">
                            <h3 className="text-sm font-medium text-red-400 sticky top-0 backdrop-blur-md py-2 z-10">Urgent Updates</h3>
                            {urgentUpdates.map(update => (
                              <UpdateCard key={update.id} update={update} />
                            ))}
                          </div>
                        )}
                        {importantUpdates.length > 0 && (
                          <div className="space-y-2">
                            <h3 className="text-sm font-medium text-yellow-400 sticky top-0 backdrop-blur-md py-2 z-10">Important Updates</h3>
                            {importantUpdates.map(update => (
                              <UpdateCard key={update.id} update={update} />
                            ))}
                          </div>
                        )}
                        {fyiUpdates.length > 0 && (
                          <div className="space-y-2">
                            <h3 className="text-sm font-medium text-blue-400 sticky top-0 backdrop-blur-md py-2 z-10">FYI</h3>
                            {fyiUpdates.map(update => (
                              <UpdateCard key={update.id} update={update} />
                            ))}
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-center py-8 text-ethereal-silver/70">
                        No updates available
                      </div>
                    )}
                  </div>
                </section>

                <section className="glass-card rounded-lg p-6">
                  <h2 className="text-xl font-semibold mb-4 mystic-text">Your Active Delegations</h2>
                  <div className="space-y-4">
                    {delegationsData?.active_delegations.length ? (
                      delegationsData.active_delegations.map((delegation, i) => (
                        <div key={`${delegation.dao_slug}-${i}`} className="glass-card p-4 rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <h3 className="font-medium mystic-text">{delegation.dao_name}</h3>
                          </div>
                          <p className="text-sm text-ethereal-silver/70">{delegation.token_amount}</p>
                          {delegation.has_active_proposals && (
                            <div className="mt-2 text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400 inline-block">
                              Active Proposals
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-ethereal-silver/70">
                        You haven't delegated to any DAOs yet
                      </div>
                    )}
                  </div>
                </section>
              </div>

              <section className="glass-card rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4 mystic-text">Available Delegations</h2>
                <p className="text-ethereal-silver/70 mb-4">DAOs where you hold tokens and can delegate your voting power</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {delegationsData?.available_delegations?.length ? (
                    delegationsData.available_delegations.map((delegation, i) => (
                      <div key={`${delegation.dao_slug}-${i}`}>
                        {renderDaoCard(delegation)}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-ethereal-silver/70">
                      No DAOs found where you can delegate
                    </div>
                  )}
                </div>
              </section>

              <section className="glass-card rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4 mystic-text">Discover More DAOs</h2>
                <p className="text-ethereal-silver/70 mb-4">Explore these DAOs based on governance activity and community engagement</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {delegationsData?.recommended_delegations?.length ? (
                    delegationsData.recommended_delegations.map((delegation, i) => (
                      <div key={`${delegation.dao_slug}-${i}`}>
                        {renderDaoCard(delegation)}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-ethereal-silver/70">
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