/**
 * Dashboard Page
 * Main overview with key metrics and recent escalations
 */
import { useQuery } from '@tanstack/react-query';
import {
    AlertTriangle,
    Clock,
    CheckCircle,
    TrendingUp,
    AlertCircle,
    ArrowRight,
    Calendar
} from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { Link } from 'react-router-dom';

import Header from '../components/layout/Header';
import { analyticsApi } from '../api/analytics';
import { escalationsApi } from '../api/escalations';
import { formatNumber, getStatusClass, getPriorityClass, formatStatus, formatPriority, formatRelativeTime } from '../utils/formatters';
import { useAuthStore } from '../stores/authStore';

function StatCard({
    label,
    value,
    icon,
    trend,
    color = 'primary'
}: {
    label: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: string;
    color?: 'primary' | 'success' | 'warning' | 'danger';
}) {
    const colorClasses = {
        primary: 'from-primary-500/20 to-primary-600/10 border-primary-500/30',
        success: 'from-success-500/20 to-success-600/10 border-success-500/30',
        warning: 'from-warning-500/20 to-warning-600/10 border-warning-500/30',
        danger: 'from-danger-500/20 to-danger-600/10 border-danger-500/30',
    };

    const iconColors = {
        primary: 'text-primary-400',
        success: 'text-success-500',
        warning: 'text-warning-500',
        danger: 'text-danger-500',
    };

    return (
        <div className={`glass-card p-6 bg-gradient-to-br ${colorClasses[color]} border`}>
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-slate-400">{label}</p>
                    <p className="text-3xl font-bold text-white mt-1">{formatNumber(Number(value))}</p>
                    {trend && (
                        <p className="text-sm text-slate-500 mt-2 flex items-center gap-1">
                            <TrendingUp size={14} />
                            {trend}
                        </p>
                    )}
                </div>
                <div className={`p-3 rounded-lg bg-slate-800/50 ${iconColors[color]}`}>
                    {icon}
                </div>
            </div>
        </div>
    );
}

export default function DashboardPage() {
    const { user } = useAuthStore();
    const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager';

    // Fetch dashboard stats (managers/admins only)
    const { data: stats, isLoading: statsLoading } = useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: analyticsApi.getDashboardStats,
        enabled: isManagerOrAdmin,
    });

    // Fetch recent escalations
    const { data: recentEscalations, isLoading: escalationsLoading } = useQuery({
        queryKey: ['recent-escalations'],
        queryFn: () => escalationsApi.getAll({ pageSize: 5 }),
    });

    return (
        <div className="min-h-screen">
            <Header title="Dashboard" />

            <div className="p-6 space-y-6">
                {/* Welcome message */}
                <div className="glass-card p-6 bg-gradient-to-r from-primary-900/30 to-violet-900/30">
                    <h2 className="text-2xl font-bold text-white">
                        Welcome back, {user?.fullName?.split(' ')[0]}!
                    </h2>
                    <p className="text-slate-400 mt-1">
                        Here's what's happening with your escalations today.
                    </p>
                </div>

                {/* Analytical Trends Section */}
                {isManagerOrAdmin && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="glass-card lg:col-span-2">
                            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                                <h3 className="font-semibold text-white flex items-center gap-2">
                                    <Calendar size={18} className="text-primary-400" />
                                    Escalation Peaks
                                </h3>
                                <Link to="/analytics" className="text-xs text-primary-400 hover:text-primary-300">View detailed analytics</Link>
                            </div>
                            <div className="p-4 h-[240px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={stats?.dailyTrends}>
                                        <defs>
                                            <linearGradient id="colorCountDash" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                        <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                                        <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                                        />
                                        <Area type="monotone" dataKey="count" stroke="#6366f1" fillOpacity={1} fill="url(#colorCountDash)" name="New Escalations" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="glass-card">
                            <div className="p-4 border-b border-slate-800">
                                <h3 className="font-semibold text-white flex items-center gap-2">
                                    <Clock size={18} className="text-violet-400" />
                                    Resolution Trend (Hrs)
                                </h3>
                            </div>
                            <div className="p-4 h-[240px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={stats?.dailyTrends}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                        <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                                        <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                                        />
                                        <Line type="monotone" dataKey="avgResolutionTime" stroke="#a855f7" strokeWidth={2} dot={false} name="Avg. Time" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                )}

                {/* Stats grid (managers/admins only) */}
                {isManagerOrAdmin && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {statsLoading ? (
                            <>
                                {[...Array(4)].map((_, i) => (
                                    <div key={i} className="glass-card p-6 animate-pulse">
                                        <div className="h-4 bg-slate-700 rounded w-1/2 mb-3" />
                                        <div className="h-8 bg-slate-700 rounded w-1/3" />
                                    </div>
                                ))}
                            </>
                        ) : stats ? (
                            <>
                                <StatCard
                                    label="Total Escalations"
                                    value={stats.totalEscalations}
                                    icon={<AlertTriangle size={24} />}
                                    trend={`${stats.escalationsThisWeek} this week`}
                                    color="primary"
                                />
                                <StatCard
                                    label="Open"
                                    value={stats.openEscalations}
                                    icon={<Clock size={24} />}
                                    color="warning"
                                />
                                <StatCard
                                    label="Resolved"
                                    value={stats.resolvedEscalations}
                                    icon={<CheckCircle size={24} />}
                                    color="success"
                                />
                                <StatCard
                                    label="Overdue"
                                    value={stats.overdueEscalations}
                                    icon={<AlertCircle size={24} />}
                                    color="danger"
                                />
                            </>
                        ) : null}
                    </div>
                )}

                {/* Recent escalations */}
                <div className="glass-card">
                    <div className="flex items-center justify-between p-4 border-b border-slate-800">
                        <h3 className="text-lg font-semibold text-white">Recent Escalations</h3>
                        <Link
                            to="/escalations"
                            className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
                        >
                            View all <ArrowRight size={16} />
                        </Link>
                    </div>

                    {escalationsLoading ? (
                        <div className="p-4 space-y-3">
                            {[...Array(5)].map((_, i) => (
                                <div key={i} className="animate-pulse flex items-center gap-4">
                                    <div className="h-12 w-12 bg-slate-700 rounded-lg" />
                                    <div className="flex-1">
                                        <div className="h-4 bg-slate-700 rounded w-2/3 mb-2" />
                                        <div className="h-3 bg-slate-700 rounded w-1/3" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : recentEscalations?.items.length ? (
                        <div className="divide-y divide-slate-800">
                            {recentEscalations.items.map((escalation) => (
                                <Link
                                    key={escalation.id}
                                    to={`/escalations/${escalation.id}`}
                                    className="flex items-center gap-4 p-4 hover:bg-slate-800/50 transition-colors"
                                >
                                    <div className={`w-1 h-12 rounded-full ${escalation.priority === 'critical' ? 'bg-danger-500' :
                                        escalation.priority === 'high' ? 'bg-orange-500' :
                                            escalation.priority === 'medium' ? 'bg-warning-500' :
                                                'bg-slate-500'
                                        }`} />
                                    <div className="flex-1 min-w-0">
                                        <p className="text-white font-medium truncate">{escalation.title}</p>
                                        <p className="text-sm text-slate-400 truncate">
                                            {escalation.clientName} • {formatRelativeTime(escalation.createdAt)}
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className={`badge ${getStatusClass(escalation.status)}`}>
                                            {formatStatus(escalation.status)}
                                        </span>
                                        <span className={`badge ${getPriorityClass(escalation.priority)}`}>
                                            {formatPriority(escalation.priority)}
                                        </span>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <div className="p-8 text-center text-slate-500">
                            No escalations found
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
