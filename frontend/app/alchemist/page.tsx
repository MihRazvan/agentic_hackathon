'use client';

import { useState } from 'react';
import { Send } from 'lucide-react';
import Image from 'next/image';

export default function AlchemistPage() {
    const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([
        {
            role: 'assistant',
            content: 'Greetings, seeker of wisdom. I am the Alchemist, your guide through the intricate realm of DAOs. How may I illuminate your path today?'
        }
    ]);
    const [input, setInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        setMessages(prev => [...prev, { role: 'user', content: input }]);
        setInput('');

        // Placeholder for actual API call
        setTimeout(() => {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'This is a placeholder response. The Alchemist AI will be integrated soon.'
            }]);
        }, 1000);
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
                                className="flex-1 bg-mystic-blue/20 text-ethereal-silver placeholder-ethereal-silver/50 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-ethereal-silver/20"
                            />
                            <button
                                type="submit"
                                className="glass-card p-2 rounded-lg hover:bg-card-hover transition-all"
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
                            <h2 className="text-xl font-semibold mystic-text mb-4">Example prompts</h2>
                            <div className="space-y-4">
                                {[
                                    'break down the implications of Proposal X',
                                    'what would happen if Proposal X passes?',
                                    'execute my vote for Proposal X',
                                    'notify me on upcoming news regarding DAO X via email'
                                ].map((prompt, index) => (
                                    <div
                                        key={index}
                                        className="glass-card p-4 rounded-lg cursor-pointer hover:bg-card-hover transition-all"
                                        onClick={() => setInput(prompt)}
                                    >
                                        <p className="text-sm text-ethereal-silver/70">
                                            {index + 1}. {prompt}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}