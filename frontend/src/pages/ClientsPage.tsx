/**
 * Clients Page
 * List and manage clients
 */
import { useQuery } from '@tanstack/react-query';
import { Building2, Plus, Search } from 'lucide-react';
import { useState } from 'react';

import Header from '../components/layout/Header';
import { clientsApi } from '../api/clients';
import { useAuthStore } from '../stores/authStore';
import { formatDate } from '../utils/formatters';

export default function ClientsPage() {
    const { user } = useAuthStore();
    const [searchQuery, setSearchQuery] = useState('');

    const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager';

    const { data: clients, isLoading } = useQuery({
        queryKey: ['clients'],
        queryFn: clientsApi.getAll,
    });

    const filteredClients = clients?.filter(client =>
        client.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        client.emailDomain?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen">
            <Header title="Clients" />

            <div className="p-6 space-y-6">
                {/* Search and actions */}
                <div className="flex flex-col md:flex-row gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search clients..."
                            className="input-field pl-10"
                        />
                    </div>
                    {isManagerOrAdmin && (
                        <button className="btn-primary flex items-center gap-2">
                            <Plus size={18} />
                            Add Client
                        </button>
                    )}
                </div>

                {/* Clients grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {isLoading ? (
                        [...Array(6)].map((_, i) => (
                            <div key={i} className="glass-card p-6 animate-pulse">
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="w-12 h-12 bg-slate-700 rounded-lg" />
                                    <div className="flex-1">
                                        <div className="h-4 bg-slate-700 rounded w-3/4 mb-2" />
                                        <div className="h-3 bg-slate-700 rounded w-1/2" />
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : filteredClients?.length ? (
                        filteredClients.map((client) => (
                            <div key={client.id} className="glass-card p-6 hover:border-primary-500/30 transition-colors">
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center">
                                        <Building2 className="text-primary-400" size={24} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-lg font-semibold text-white truncate">{client.name}</h3>
                                        <p className="text-sm text-slate-400 truncate">
                                            {client.emailDomain || 'No domain'}
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-4 pt-4 border-t border-slate-800">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-slate-500">Industry</span>
                                        <span className="text-slate-300">{client.industry || '-'}</span>
                                    </div>
                                    <div className="flex justify-between text-sm mt-2">
                                        <span className="text-slate-500">Risk Score</span>
                                        <span className={`font-medium ${client.riskScore > 0.7 ? 'text-danger-500' :
                                                client.riskScore > 0.4 ? 'text-warning-500' :
                                                    'text-success-500'
                                            }`}>
                                            {(client.riskScore * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm mt-2">
                                        <span className="text-slate-500">Added</span>
                                        <span className="text-slate-300">{formatDate(client.createdAt)}</span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="col-span-full text-center py-12 text-slate-500">
                            No clients found
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
