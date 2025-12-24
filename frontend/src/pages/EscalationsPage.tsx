/**
 * Escalations Page
 * List view with filtering and status management
 */
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Filter, Plus, Search, AlertTriangle } from 'lucide-react';

import Header from '../components/layout/Header';
import { escalationsApi } from '../api/escalations';
import { useFilterStore } from '../stores/filterStore';
import { useAuthStore } from '../stores/authStore';
import {
    formatDate,
    formatStatus,
    formatPriority,
    getStatusClass,
    getPriorityClass
} from '../utils/formatters';
import type { EscalationStatus, EscalationPriority } from '../types';

export default function EscalationsPage() {
    const { user } = useAuthStore();
    const { filters, setFilter, setPage, resetFilters } = useFilterStore();
    const [searchQuery, setSearchQuery] = useState('');

    const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager';

    // Fetch escalations with filters
    const { data, isLoading } = useQuery({
        queryKey: ['escalations', filters],
        queryFn: () => escalationsApi.getAll(filters),
    });

    const statusOptions: { value: EscalationStatus | ''; label: string }[] = [
        { value: '', label: 'All Status' },
        { value: 'open', label: 'Open' },
        { value: 'in_progress', label: 'In Progress' },
        { value: 'resolved', label: 'Resolved' },
    ];

    const priorityOptions: { value: EscalationPriority | ''; label: string }[] = [
        { value: '', label: 'All Priority' },
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' },
        { value: 'critical', label: 'Critical' },
    ];

    return (
        <div className="min-h-screen">
            <Header title="Escalations" />

            <div className="p-6 space-y-6">
                {/* Filters bar */}
                <div className="glass-card p-4">
                    <div className="flex flex-col lg:flex-row gap-4">
                        {/* Search */}
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search escalations..."
                                className="input-field pl-10"
                            />
                        </div>

                        {/* Status filter */}
                        <div className="flex items-center gap-2">
                            <Filter size={16} className="text-slate-500" />
                            <select
                                value={filters.status || ''}
                                onChange={(e) => setFilter('status', e.target.value as EscalationStatus || undefined)}
                                className="input-field w-40"
                            >
                                {statusOptions.map((opt) => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                ))}
                            </select>
                        </div>

                        {/* Priority filter */}
                        <select
                            value={filters.priority || ''}
                            onChange={(e) => setFilter('priority', e.target.value as EscalationPriority || undefined)}
                            className="input-field w-40"
                        >
                            {priorityOptions.map((opt) => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>

                        {/* Reset */}
                        <button onClick={resetFilters} className="btn-secondary">
                            Reset
                        </button>

                        {/* Create (managers only) */}
                        {isManagerOrAdmin && (
                            <Link to="/escalations/new" className="btn-primary flex items-center gap-2">
                                <Plus size={18} />
                                New Escalation
                            </Link>
                        )}
                    </div>
                </div>

                {/* Escalations table */}
                <div className="glass-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-800">
                                    <th className="text-left p-4 text-sm font-medium text-slate-400">Title</th>
                                    <th className="text-left p-4 text-sm font-medium text-slate-400">Client</th>
                                    <th className="text-left p-4 text-sm font-medium text-slate-400">Project</th>
                                    <th className="text-left p-4 text-sm font-medium text-slate-400">Status</th>
                                    <th className="text-left p-4 text-sm font-medium text-slate-400">Priority</th>
                                    <th className="text-left p-4 text-sm font-medium text-slate-400">Assignee</th>
                                    <th className="text-left p-4 text-sm font-medium text-slate-400">Due Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {isLoading ? (
                                    [...Array(5)].map((_, i) => (
                                        <tr key={i} className="border-b border-slate-800">
                                            {[...Array(6)].map((_, j) => (
                                                <td key={j} className="p-4">
                                                    <div className="h-4 bg-slate-700 rounded animate-pulse" />
                                                </td>
                                            ))}
                                        </tr>
                                    ))
                                ) : data?.items.length ? (
                                    data.items.map((escalation) => (
                                        <tr
                                            key={escalation.id}
                                            className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors cursor-pointer"
                                        >
                                            <td className="p-4">
                                                <Link
                                                    to={`/escalations/${escalation.id}`}
                                                    className="text-white hover:text-primary-400 font-medium"
                                                >
                                                    <div className="flex items-center gap-2">
                                                        {escalation.isOverdue && (
                                                            <AlertTriangle size={16} className="text-danger-500" />
                                                        )}
                                                        <span className="truncate max-w-xs">{escalation.title}</span>
                                                    </div>
                                                </Link>
                                            </td>
                                            <td className="p-4 text-slate-400">{escalation.clientName || '-'}</td>
                                            <td className="p-4 text-slate-400 text-sm">
                                                {escalation.projectName || '-'}
                                                {escalation.departmentName && (
                                                    <div className="text-xs text-slate-600">{escalation.departmentName}</div>
                                                )}
                                            </td>
                                            <td className="p-4">
                                                <span className={`badge ${getStatusClass(escalation.status)}`}>
                                                    {formatStatus(escalation.status)}
                                                </span>
                                            </td>
                                            <td className="p-4">
                                                <span className={`badge ${getPriorityClass(escalation.priority)}`}>
                                                    {formatPriority(escalation.priority)}
                                                </span>
                                            </td>
                                            <td className="p-4 text-slate-400">
                                                {escalation.assigneeName || (
                                                    <span className="text-slate-600 italic">Unassigned</span>
                                                )}
                                            </td>
                                            <td className="p-4">
                                                <span className={escalation.isOverdue ? 'text-danger-500' : 'text-slate-400'}>
                                                    {formatDate(escalation.dueDate)}
                                                </span>
                                                {escalation.daysUntilDue > 0 && escalation.daysUntilDue <= 7 && !escalation.isOverdue && (
                                                    <span className="ml-2 text-xs text-warning-500">
                                                        ({escalation.daysUntilDue}d left)
                                                    </span>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={6} className="p-8 text-center text-slate-500">
                                            No escalations found
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    {data && data.totalPages > 1 && (
                        <div className="flex items-center justify-between p-4 border-t border-slate-800">
                            <p className="text-sm text-slate-400">
                                Showing {((data.page - 1) * data.pageSize) + 1} to {Math.min(data.page * data.pageSize, data.total)} of {data.total}
                            </p>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setPage(data.page - 1)}
                                    disabled={data.page <= 1}
                                    className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Previous
                                </button>
                                <button
                                    onClick={() => setPage(data.page + 1)}
                                    disabled={data.page >= data.totalPages}
                                    className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
