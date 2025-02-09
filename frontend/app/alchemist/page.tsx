'use client';

import { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import Image from 'next/image';
import { useAccount, useWalletClient, useSwitchChain, usePublicClient } from 'wagmi';
import { parseUnits } from 'viem';
import { base } from 'viem/chains';

// Hardcoded Seamless Protocol configuration
const SEAMLESS_CONFIG = {
    name: "Seamless Protocol",
    token: {
        address: "0x1c7a460413dd4e964f96d8dfc56e7223ce88cd85",
        symbol: "SEAM",
        decimals: 18
    }
};

// ABIs
const TOKEN_ABI = [
    {
        "inputs": [
            { "name": "delegatee", "type": "address" }
        ],
        "name": "delegate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
];

export default function AlchemistPage() {
    const { address } = useAccount();
    const { data: walletClient } = useWalletClient();
    const publicClient = usePublicClient();
    const { switchChain } = useSwitchChain();
    const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([
        {
            role: 'assistant',
            content: 'Greetings, seeker of wisdom. I am the Alchemist, your guide through the intricate realm of DAOs. Ask me about governance proposals, treasury allocations, or delegate your voting power to shape the future of decentralized organizations.'
        }
    ]);
    const [input, setInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);

    const handleDelegation = async (amount: string) => {
        if (!walletClient || !address || !publicClient) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Please connect your wallet first.'
            }]);
            return;
        }

        try {
            setIsProcessing(true);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Initiating delegation of ${amount} SEAM to Seamless Protocol...`
            }]);

            // Switch to Base chain first
            try {
                await switchChain({ chainId: base.id });
            } catch (error) {
                throw new Error('Please switch your wallet to the Base network to continue.');
            }

            // Execute the delegation directly on the token contract
            const delegateTx = await walletClient.writeContract({
                chain: base,
                address: SEAMLESS_CONFIG.token.address as `0x${string}`,
                abi: TOKEN_ABI,
                functionName: 'delegate',
                args: [address] // Delegate to self
            });

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Delegation transaction submitted: ${delegateTx}`
            }]);

            // Wait for delegation to be mined
            await publicClient.waitForTransactionReceipt({ hash: delegateTx });

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Delegation successful! Your transaction has been confirmed.`
            }]);

        } catch (error) {
            console.error('Delegation error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Error during delegation: ${error.message}`
            }]);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input.trim();
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setInput('');

        // Check for delegation command
        const delegateMatch = userMessage.toLowerCase().match(/^delegate (\d+) seam to seamless protocol$/i);
        if (delegateMatch) {
            const [_, amount] = delegateMatch;
            await handleDelegation(amount);
        } else if (userMessage.toLowerCase().includes('implications') || userMessage.toLowerCase().includes('proposal')) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Analyzing proposal implications requires access to on-chain data. Please connect your wallet to proceed with the analysis.'
            }]);
        } else if (userMessage.toLowerCase().includes('treasury')) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'To analyze treasury allocations, I need access to your DAO memberships. Please connect your wallet to proceed.'
            }]);
        } else {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'I can help you with:\n- Analyzing proposal implications\n- Predicting governance outcomes\n- Reviewing treasury allocations\n- Delegating voting power\n\nWhat would you like to know?'
            }]);
        }
    };

    return (
        <div className="min-h-screen pt-16">
            <div className="max-w-7xl mx-auto p-4">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-8rem)]">
                    {/* Chat Interface */}
                    <div className="glass-card rounded-lg p-6 flex flex-col">
                        <div className="flex-1 overflow-y-auto space-y-4 scrollbar-thin mb-4">
                            {messages.map((message, index) => (
                                <div
                                    key={index}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] p-4 rounded-lg ${message.role === 'user'
                                                ? 'bg-mystic-blue text-ethereal-silver ml-4'
                                                : 'bg-arcane-purple/30 text-ethereal-silver mr-4'
                                            }`}
                                    >
                                        {message.content}
                                    </div>
                                </div>
                            ))}
                        </div>
                        <form onSubmit={handleSubmit} className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Invoke the Alchemist's wisdom..."
                                className="flex-1 bg-white text-black placeholder-gray-500 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-ethereal-silver/20"
                                disabled={isProcessing}
                            />
                            <button
                                type="submit"
                                className="glass-card p-2 rounded-lg hover:bg-card-hover transition-all disabled:opacity-50"
                                disabled={isProcessing}
                            >
                                <Send className="w-6 h-6 text-ethereal-silver" />
                            </button>
                        </form>
                    </div>

                    {/* Information Panel */}
                    <div className="glass-card rounded-lg p-6 flex flex-col">
                        <div className="mb-8 text-center">
                            <Image
                                src="/big icon alchemist.png"
                                alt="Alchemist"
                                width={200}
                                height={200}
                                className="mx-auto mb-6"
                            />
                            <h1 className="text-4xl font-bold mystic-text mb-2">ALCHEMIST</h1>
                            <p className="text-ethereal-silver/70">
                                Neither bound by time nor swayed by bias, it analyzes, predicts, and acts
                                prompted by those who seek to influence the future.
                            </p>
                        </div>

                        <div className="space-y-6">
                            <h2 className="text-xl font-semibold mystic-text mb-4">Available Commands</h2>
                            <div className="space-y-4">
                                <div
                                    className="glass-card p-4 rounded-lg cursor-pointer hover:bg-card-hover transition-all"
                                    onClick={() => setInput('delegate 5 SEAM to Seamless Protocol')}
                                >
                                    <p className="text-sm text-ethereal-silver/70">
                                        delegate 5 SEAM to Seamless Protocol
                                    </p>
                                </div>
                                <div
                                    className="glass-card p-4 rounded-lg cursor-pointer hover:bg-card-hover transition-all"
                                    onClick={() => setInput('Break down the implications of my last active proposal')}
                                >
                                    <p className="text-sm text-ethereal-silver/70">
                                        Break down the implications of my last active proposal
                                    </p>
                                </div>
                                <div
                                    className="glass-card p-4 rounded-lg cursor-pointer hover:bg-card-hover transition-all"
                                    onClick={() => setInput('What would happen if this proposal passes?')}
                                >
                                    <p className="text-sm text-ethereal-silver/70">
                                        What would happen if this proposal passes?
                                    </p>
                                </div>
                                <div
                                    className="glass-card p-4 rounded-lg cursor-pointer hover:bg-card-hover transition-all"
                                    onClick={() => setInput("Show me my active DAO's treasury allocation")}
                                >
                                    <p className="text-sm text-ethereal-silver/70">
                                        Show me my active DAO's treasury allocation
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}