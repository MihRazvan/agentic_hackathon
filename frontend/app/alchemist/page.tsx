'use client';

import { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import Image from 'next/image';
import { useAccount, useWalletClient, useSwitchChain } from 'wagmi';
import { parseUnits } from 'viem';
import { base } from 'viem/chains';

// Hardcoded Seamless Protocol configuration
const SEAMLESS_CONFIG = {
    name: "Seamless Protocol",
    token: {
        address: "0x1c7a460413dd4e964f96d8dfc56e7223ce88cd85",
        symbol: "SEAM",
        decimals: 18
    },
    delegation: {
        // Fixed address with correct checksum
        address: "0x8578e222d144e8ac4a7e2d4d19696b4a45d3c382",
        defaultDelegate: "0x8F9DF4115ac301d0e7dd087c270C2282fC7336ab"
    }
};

// ABIs
const TOKEN_ABI = [
    {
        "inputs": [
            { "name": "spender", "type": "address" },
            { "name": "amount", "type": "uint256" }
        ],
        "name": "approve",
        "outputs": [{ "name": "", "type": "bool" }],
        "stateMutability": "nonpayable",
        "type": "function"
    }
];

const DELEGATION_ABI = [
    {
        "inputs": [
            { "name": "delegatee", "type": "address" },
            { "name": "amount", "type": "uint256" }
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
    const { switchChain } = useSwitchChain();
    const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([
        {
            role: 'assistant',
            content: 'Greetings, seeker of wisdom. I am the Alchemist, your guide through the intricate realm of DAOs. I can help you delegate your SEAM tokens to Seamless Protocol. Try saying: "delegate 10 SEAM to Seamless Protocol"'
        }
    ]);
    const [input, setInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);

    const handleDelegation = async (amount: string) => {
        if (!walletClient || !address) {
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

            // Parse amount to wei
            const parsedAmount = parseUnits(amount, SEAMLESS_CONFIG.token.decimals);

            // 1. Approve the delegation contract
            const approveTx = await walletClient.writeContract({
                chain: base,
                address: SEAMLESS_CONFIG.token.address as `0x${string}`,
                abi: TOKEN_ABI,
                functionName: 'approve',
                args: [SEAMLESS_CONFIG.delegation.address, parsedAmount]
            });

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Approval transaction submitted: ${approveTx}`
            }]);

            // Wait for approval to be mined
            await walletClient.waitForTransactionReceipt({ hash: approveTx });

            // 2. Execute the delegation
            const delegateTx = await walletClient.writeContract({
                chain: base,
                address: SEAMLESS_CONFIG.delegation.address as `0x${string}`,
                abi: DELEGATION_ABI,
                functionName: 'delegate',
                args: [SEAMLESS_CONFIG.delegation.defaultDelegate, parsedAmount]
            });

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Delegation successful! Transaction hash: ${delegateTx}`
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
        } else {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'I understand delegation commands in the format: "delegate [amount] SEAM to Seamless Protocol". For example: "delegate 10 SEAM to Seamless Protocol"'
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
                                className="flex-1 bg-mystic-blue/20 text-black placeholder-ethereal-silver/50 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-ethereal-silver/20"
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
                                    onClick={() => setInput('delegate 10 SEAM to Seamless Protocol')}
                                >
                                    <p className="text-sm text-ethereal-silver/70">
                                        delegate 10 SEAM to Seamless Protocol
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