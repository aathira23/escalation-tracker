import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import {
    ArrowLeft,
    Calendar,
    User as UserIcon,
    MessageSquare,
    CheckCircle,
    Clock,
    AlertCircle,
    Sparkles,
    Briefcase,
    Building
} from 'lucide-react';
import toast from 'react-hot-toast';

import Header from '../components/layout/Header';
import { escalationsApi } from '../api/escalations';
import { usersApi } from '../api/users';
import { useAuthStore } from '../stores/authStore';
import {
    formatDate,
    formatStatus,
    formatPriority,
    getStatusClass,
    getPriorityClass
} from '../utils/formatters';
import type { EscalationStatus } from '../types';

export default function EscalationDetailPage() {
    const { id } = useParams<{ id: string }>();
    const { user, token } = useAuthStore();
    const queryClient = useQueryClient();
    const [noteContent, setNoteContent] = useState('');

    const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager';

    // Fetch escalation details
    const { data: escalation, isLoading, error } = useQuery({
        queryKey: ['escalation', id],
        queryFn: () => escalationsApi.getById(id!),
        enabled: !!id,
    });

    // Fetch timeline
    const { data: timeline } = useQuery({
        queryKey: ['timeline', id],
        queryFn: () => escalationsApi.getTimeline(id!),
        enabled: !!id,
    });

    // Fetch available resolvers for manual assignment
    const { data: availableResolvers } = useQuery({
        queryKey: ['available-resolvers'],
        queryFn: usersApi.getAvailableResolvers,
        enabled: isManagerOrAdmin,
    });

    const { data: notes } = useQuery({
        queryKey: ['notes', id],
        queryFn: () => escalationsApi.getNotes(id!),
        enabled: !!id,
    });

    // Mutations
    const statusMutation = useMutation({
        mutationFn: (newStatus: EscalationStatus) =>
            escalationsApi.updateStatus(id!, { status: newStatus }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['escalation', id] });
            queryClient.invalidateQueries({ queryKey: ['timeline', id] });
            queryClient.invalidateQueries({ queryKey: ['notes', id] });
            toast.success('Status updated successfully');
        },
        onError: (err: any) => {
            toast.error(err.response?.data?.detail || 'Failed to update status');
        }
    });

    const noteMutation = useMutation({
        mutationFn: (content: string) =>
            escalationsApi.addNote(id!, { content }),
        onSuccess: () => {
            setNoteContent('');
            queryClient.invalidateQueries({ queryKey: ['escalation', id] });
            queryClient.invalidateQueries({ queryKey: ['timeline', id] });
            queryClient.invalidateQueries({ queryKey: ['notes', id] });
            toast.success('Note added');
        },
    });

    const { data: recommendations } = useQuery({
        queryKey: ['escalation-recommendations', id],
        queryFn: () => escalationsApi.getRecommendations(id!),
        enabled: !!id && isManagerOrAdmin,
    });

    const assignMutation = useMutation({
        mutationFn: (assigneeId: string) =>
            escalationsApi.assign(id!, { assignee_id: assigneeId }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['escalation', id] });
            queryClient.invalidateQueries({ queryKey: ['timeline', id] });
            toast.success('Assignee updated');
        },
        onError: (err: any) => {
            toast.error(err.response?.data?.detail || 'Failed to assign');
        }
    });

    // WebSocket for real-time updates
    useEffect(() => {
        if (!token || !id) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws?token=${token}`;
        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.escalation_id === id) {
                queryClient.invalidateQueries({ queryKey: ['escalation', id] });
                queryClient.invalidateQueries({ queryKey: ['timeline', id] });

                if (message.type === 'escalation_status_updated') {
                    toast(`${message.updated_by_name} updated status to ${message.status}`, { icon: '🔄' });
                } else if (message.type === 'escalation_assigned') {
                    toast(`${message.assigned_by_name} assigned this to ${message.assignee_name}`, { icon: '👤' });
                }
            }
        };

        return () => ws.close();
    }, [id, token, queryClient]);

    if (isLoading) return <div className="p-10 text-center text-slate-400">Loading escalation...</div>;
    if (error || !escalation) return <div className="p-10 text-center text-danger-400">Escalation not found</div>;

    const isResolver = user?.id === escalation.assignedTo;
    const canUpdateStatus = isResolver || isManagerOrAdmin;

    // Filter AI resolution suggestions
    const resolutionSuggestions = escalation.aiSuggestions?.find(s => s.suggestionType === 'resolution');

    return (
        <div className="min-h-screen">
            <Header title="Escalation Details" />

            <div className="p-6 max-w-7xl mx-auto space-y-6">
                {/* Navigation and Actions */}
                <div className="flex items-center justify-between">
                    <Link to="/escalations" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
                        <ArrowLeft size={20} />
                        Back to List
                    </Link>

                    <div className="flex gap-3">
                        {canUpdateStatus && escalation.status !== 'resolved' && (
                            <button
                                onClick={() => statusMutation.mutate('resolved')}
                                className="btn-primary flex items-center gap-2"
                            >
                                <CheckCircle size={18} />
                                Mark Resolved
                            </button>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Title Card */}
                        <div className="glass-card p-6">
                            <div className="flex justify-between items-start mb-4">
                                <span className={`badge ${getPriorityClass(escalation.priority)}`}>
                                    {formatPriority(escalation.priority)} Priority
                                </span>
                                <span className={`badge ${getStatusClass(escalation.status)}`}>
                                    {formatStatus(escalation.status)}
                                </span>
                            </div>
                            <h1 className="text-2xl font-bold text-white mb-2">{escalation.title}</h1>
                            <p className="text-slate-400 whitespace-pre-wrap">{escalation.description}</p>

                            {escalation.executiveSummary && (
                                <div className="mt-6 p-4 bg-primary-500/10 border border-primary-500/20 rounded-lg">
                                    <div className="flex items-center gap-2 text-primary-400 font-medium mb-1">
                                        <Sparkles size={16} />
                                        AI Executive Summary
                                    </div>
                                    <p className="text-slate-300 text-sm italic">{escalation.executiveSummary}</p>
                                </div>
                            )}
                        </div>

                        {/* AI Resolution Recommendations */}
                        {resolutionSuggestions && (
                            <div className="glass-card p-6 border-l-4 border-accent-500">
                                <div className="flex items-center gap-2 text-accent-400 font-semibold mb-4">
                                    <Sparkles size={18} />
                                    AI Suggested Resolution Steps
                                </div>
                                <div className="space-y-3">
                                    {resolutionSuggestions.content.steps.map((step: string, idx: number) => (
                                        <div key={idx} className="flex gap-3 items-start p-3 bg-slate-800/50 rounded-lg">
                                            <div className="h-6 w-6 rounded-full bg-accent-500/20 text-accent-400 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                                                {idx + 1}
                                            </div>
                                            <p className="text-slate-300 text-sm">{step}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Timeline / Activity */}
                        <div className="glass-card p-6">
                            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                                <Clock size={20} className="text-slate-400" />
                                Activity Timeline
                            </h2>
                            <div className="space-y-6">
                                {timeline?.map((event, idx) => (
                                    <div key={event.id} className="relative pl-8 pb-6 last:pb-0">
                                        {idx !== timeline.length - 1 && (
                                            <div className="absolute left-[11px] top-[24px] bottom-0 w-[2px] bg-slate-800" />
                                        )}
                                        <div className="absolute left-0 top-1 h-6 w-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center">
                                            <div className="h-2 w-2 rounded-full bg-primary-500" />
                                        </div>
                                        <div className="flex flex-col">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-white font-medium text-sm">{event.description}</span>
                                                <span className="text-slate-500 text-xs">• {formatDate(event.createdAt)}</span>
                                            </div>
                                            <span className="text-slate-500 text-xs">by {event.userName || 'System'}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Info Card */}
                        <div className="glass-card p-6 divide-y divide-slate-800">
                            <div className="pb-4 space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-slate-800 rounded-lg">
                                        <Building size={18} className="text-slate-400" />
                                    </div>
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider">Client</div>
                                        <div className="text-white font-medium">{escalation.clientName}</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-slate-800 rounded-lg">
                                        <Briefcase size={18} className="text-slate-400" />
                                    </div>
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider">Project / Dept</div>
                                        <div className="text-white font-medium">
                                            {escalation.projectName}
                                            <span className="text-slate-500 text-sm ml-1">({escalation.departmentName})</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="py-4 space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-slate-800 rounded-lg">
                                        <UserIcon size={18} className="text-slate-400" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-xs text-slate-500 uppercase tracking-wider">Assignee</div>
                                        {isManagerOrAdmin ? (
                                            <div className="mt-1">
                                                <select
                                                    className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-white focus:outline-none focus:border-primary-500"
                                                    value={escalation.assignedTo || ''}
                                                    onChange={(e) => {
                                                        if (e.target.value) assignMutation.mutate(e.target.value);
                                                    }}
                                                    disabled={assignMutation.isPending}
                                                >
                                                    <option value="">Unassigned</option>
                                                    {availableResolvers?.map(res => (
                                                        <option key={res.id} value={res.id}>{res.fullName} ({res.currentEscalationCount}/{res.maxConcurrentEscalations})</option>
                                                    ))}
                                                    {escalation.assignedTo && !availableResolvers?.find(r => r.id === escalation.assignedTo) && (
                                                        <option value={escalation.assignedTo}>{escalation.assigneeName}</option>
                                                    )}
                                                </select>
                                            </div>
                                        ) : (
                                            <div className="text-white font-medium">
                                                {escalation.assigneeName || (
                                                    <span className="text-slate-500 italic">Unassigned</span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-slate-800 rounded-lg">
                                        <Calendar size={18} className="text-slate-400" />
                                    </div>
                                    <div>
                                        <div className="text-xs text-slate-500 uppercase tracking-wider">SLA Due Date</div>
                                        <div className={`font-medium ${escalation.isOverdue ? 'text-danger-500' : 'text-white'}`}>
                                            {formatDate(escalation.dueDate)}
                                            {escalation.isOverdue && <span className="ml-2 text-xs">(Overdue)</span>}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="pt-4 space-y-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2 text-slate-400 text-sm">
                                        <AlertCircle size={14} />
                                        Churn Risk
                                    </div>
                                    <div className={`text-sm font-bold ${escalation.churnRisk > 0.7 ? 'text-danger-500' : 'text-success-500'}`}>
                                        {Math.round(escalation.churnRisk * 100)}%
                                    </div>
                                </div>
                                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-1000 ${escalation.churnRisk > 0.7 ? 'bg-danger-500' : 'bg-success-500'}`}
                                        style={{ width: `${escalation.churnRisk * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* AI Recommendations (For Managers) */}
                        {isManagerOrAdmin && recommendations && recommendations.length > 0 && !escalation.assignedTo && (
                            <div className="glass-card p-6 bg-primary-500/5 border-primary-500/30">
                                <div className="flex items-center gap-2 text-primary-400 font-semibold mb-4 text-sm">
                                    <Sparkles size={16} />
                                    AI Moderator Recommendations
                                </div>
                                <div className="space-y-4">
                                    {recommendations.slice(0, 3).map((rec: any) => (
                                        <div key={rec.user_id} className="p-3 rounded-lg bg-slate-900/50 border border-slate-700/50">
                                            <div className="flex justify-between items-start mb-2">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-8 h-8 rounded-full bg-primary-500/10 flex items-center justify-center text-primary-400 font-bold text-xs">
                                                        {rec.full_name.charAt(0)}
                                                    </div>
                                                    <div>
                                                        <div className="text-white text-sm font-medium">{rec.full_name}</div>
                                                        <div className="text-[10px] text-slate-500">
                                                            Workload: {rec.current_workload}/{rec.max_capacity}
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="text-xs font-bold text-primary-400">
                                                    {Math.round(rec.score * 100)}% Match
                                                </div>
                                            </div>
                                            <div className="mb-3">
                                                {rec.reasons.map((reason: string, i: number) => (
                                                    <div key={i} className="flex items-center gap-1.5 text-[10px] text-slate-400">
                                                        <CheckCircle size={10} className="text-success-500/70" />
                                                        {reason}
                                                    </div>
                                                ))}
                                            </div>
                                            <button
                                                onClick={() => assignMutation.mutate(rec.user_id)}
                                                disabled={assignMutation.isPending}
                                                className="w-full py-1.5 rounded bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 text-[10px] font-bold uppercase tracking-wider transition-colors disabled:opacity-50"
                                            >
                                                Assign This Moderator
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Notes Section */}
                        <div className="glass-card p-6">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <MessageSquare size={20} className="text-slate-400" />
                                Notes
                            </h2>

                            {/* Existing Notes List */}
                            <div className="space-y-4 mb-6 max-h-[400px] overflow-y-auto pr-2 scrollbar-thin">
                                {notes?.map((note) => (
                                    <div key={note.id} className={`p-4 rounded-lg bg-slate-800/50 border ${note.isInternal ? 'border-primary-500/20 shadow-[0_0_10px_rgba(99,102,241,0.05)]' : 'border-slate-700'}`}>
                                        <div className="flex justify-between items-start mb-2">
                                            <span className={`text-xs font-bold ${note.isInternal ? 'text-primary-400' : 'text-slate-400'}`}>
                                                {note.authorName || 'System'}
                                            </span>
                                            <span className="text-[10px] text-slate-500 uppercase tracking-tighter">
                                                {formatDate(note.createdAt)}
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">{note.content}</p>
                                    </div>
                                ))}
                                {(!notes || notes.length === 0) && (
                                    <p className="text-center text-slate-500 text-sm italic py-4">No notes entered yet</p>
                                )}
                            </div>

                            <textarea
                                value={noteContent}
                                onChange={(e) => setNoteContent(e.target.value)}
                                placeholder="Add a note or update details..."
                                className="input-field min-h-[100px] mb-4 text-sm"
                            />
                            <button
                                onClick={() => noteMutation.mutate(noteContent)}
                                disabled={!noteContent.trim() || noteMutation.isPending}
                                className="w-full btn-secondary text-sm disabled:opacity-50"
                            >
                                {noteMutation.isPending ? 'Adding...' : 'Add Note'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
