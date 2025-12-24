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

    // Mutations
    const statusMutation = useMutation({
        mutationFn: (newStatus: EscalationStatus) =>
            escalationsApi.updateStatus(id!, { status: newStatus }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['escalation', id] });
            queryClient.invalidateQueries({ queryKey: ['timeline', id] });
            toast.success('Status updated successfully');
        },
    });

    const noteMutation = useMutation({
        mutationFn: (content: string) =>
            escalationsApi.addNote(id!, { content }),
        onSuccess: () => {
            setNoteContent('');
            queryClient.invalidateQueries({ queryKey: ['escalation', id] });
            queryClient.invalidateQueries({ queryKey: ['timeline', id] });
            toast.success('Note added');
        },
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

    const isResolver = escalation.assignedTo === user?.id;
    const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager';
    const canUpdateStatus = isResolver || isManagerOrAdmin;

    // Filter AI resolution suggestions
    const resolutionSuggestions = escalation.aiSuggestions?.find(s => s.suggestionType === 'resolution');
    const assignmentSuggestions = escalation.aiSuggestions?.find(s => s.suggestionType === 'assignment');

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
                                        <div className="text-white font-medium">
                                            {escalation.assigneeName || (
                                                <span className="text-slate-500 italic">Unassigned</span>
                                            )}
                                        </div>
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

                        {/* AI Recommended Assignee (For Managers) */}
                        {isManagerOrAdmin && assignmentSuggestions && !escalation.assignedTo && (
                            <div className="glass-card p-6 bg-primary-500/5 border-primary-500/30">
                                <div className="flex items-center gap-2 text-primary-400 font-semibold mb-4 text-sm">
                                    <Sparkles size={16} />
                                    AI Assignment Suggestion
                                </div>
                                <div className="space-y-3">
                                    <div className="flex items-center gap-2 text-white text-sm font-medium">
                                        <UserIcon size={14} className="text-primary-400" />
                                        {assignmentSuggestions.content.recommended_user_name}
                                    </div>
                                    <p className="text-slate-400 text-xs italic leading-relaxed">
                                        {assignmentSuggestions.content.reason}
                                    </p>
                                    <button
                                        onClick={() => escalationsApi.assign(id!, { assignee_id: assignmentSuggestions.content.recommended_user_id }).then(() => queryClient.invalidateQueries({ queryKey: ['escalation', id] }))}
                                        className="w-full btn-primary text-xs py-2"
                                    >
                                        Accept Suggestion
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Notes Section */}
                        <div className="glass-card p-6">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <MessageSquare size={20} className="text-slate-400" />
                                Notes
                            </h2>
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
