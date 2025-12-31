/**
 * Analytics Page
 * Visual reporting and system performance insights
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    TrendingUp,
    Clock,
    Target,
    AlertTriangle,
    BarChart3,
    Calendar,
    ArrowUpRight,
    ArrowDownRight,
    Layers,
    ChevronDown,
    ExternalLink
} from 'lucide-react';
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Cell,
    PieChart,
    Pie
} from 'recharts';

import Header from '../components/layout/Header';
import { analyticsApi } from '../api/analytics';
import { formatRelativeTime } from '../utils/formatters';
import { Link } from 'react-router-dom';

const COLORS = ['#6366f1', '#a855f7', '#ec4899', '#ef4444', '#f59e0b', '#22c55e'];

function ComplaintClusters() {
    const [expandedCluster, setExpandedCluster] = useState<string | null>(null);
    const { data: clusters, isLoading } = useQuery({
        queryKey: ['complaint-clusters'],
        queryFn: analyticsApi.getClusters,
    });

    if (isLoading) return (
        <div className="glass-card p-6 animate-pulse h-[300px]" />
    );

    if (!clusters || clusters.length === 0) return null;

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 mb-2">
                <Layers size={18} className="text-primary-400" />
                <h3 className="text-lg font-semibold text-white">AI Complaint Clusters</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {clusters.map((cluster) => (
                    <div
                        key={cluster.id}
                        className={`glass-card overflow-hidden border transition-all duration-300 ${expandedCluster === cluster.id ? 'border-primary-500/50 ring-1 ring-primary-500/20' : 'border-slate-800'
                            }`}
                    >
                        <div
                            className="p-4 cursor-pointer hover:bg-white/5 flex items-start justify-between"
                            onClick={() => setExpandedCluster(expandedCluster === cluster.id ? null : cluster.id)}
                        >
                            <div className="flex-1">
                                <div className="flex items-center gap-3">
                                    <h4 className="font-bold text-white">{cluster.name}</h4>
                                    {cluster.isRecurrence && (
                                        <span className="px-1.5 py-0.5 rounded bg-danger-500/20 text-danger-400 text-[10px] font-bold uppercase tracking-wider">
                                            Recurrence
                                        </span>
                                    )}
                                    <span className="text-xs text-slate-500">{cluster.count} issues</span>
                                </div>
                                <p className="text-sm text-slate-400 mt-1">{cluster.description}</p>
                            </div>
                            <ChevronDown
                                size={18}
                                className={`text-slate-500 transition-transform ${expandedCluster === cluster.id ? 'rotate-180' : ''}`}
                            />
                        </div>

                        {expandedCluster === cluster.id && (
                            <div className="px-4 pb-4 pt-2 border-t border-slate-800/50 bg-slate-900/30">
                                <div className="space-y-2">
                                    {cluster.items.map((item) => (
                                        <Link
                                            key={item.id}
                                            to={`/escalations/${item.id}`}
                                            className="flex items-center justify-between p-2 rounded hover:bg-primary-500/10 group transition-colors"
                                        >
                                            <div className="min-w-0">
                                                <p className="text-xs font-medium text-slate-200 group-hover:text-primary-300 truncate">
                                                    {item.title}
                                                </p>
                                                <p className="text-[10px] text-slate-500">
                                                    {item.clientName || 'General'} • {formatRelativeTime(item.createdAt)}
                                                </p>
                                            </div>
                                            <ExternalLink size={12} className="text-slate-600 group-hover:text-primary-400" />
                                        </Link>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function AnalyticsPage() {
    // Fetch dashboard stats (includes trends)
    const { data: stats, isLoading } = useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: analyticsApi.getDashboardStats,
    });

    // Fetch client analytics
    const { data: clientData } = useQuery({
        queryKey: ['client-analytics'],
        queryFn: analyticsApi.getClientAnalytics,
    });

    if (isLoading) {
        return (
            <div className="min-h-screen">
                <Header title="Analytics" />
                <div className="p-6 flex items-center justify-center min-h-[400px]">
                    <div className="w-12 h-12 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
                </div>
            </div>
        );
    }

    const churnData = clientData?.clients.map(c => ({
        name: c.clientName,
        risk: c.churnRisk * 100,
        count: c.totalEscalations
    })).sort((a, b) => b.risk - a.risk).slice(0, 5) || [];

    return (
        <div className="min-h-screen">
            <Header title="Analytics & Insights" />

            <div className="p-6 space-y-6">
                {/* Performance Summary Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="glass-card p-6 border-l-4 border-primary-500">
                        <div className="flex items-center justify-between mb-4">
                            <span className="p-2 bg-primary-500/10 text-primary-400 rounded-lg">
                                <Target size={20} />
                            </span>
                            <span className="text-xs font-medium text-success-400 flex items-center gap-1">
                                <TrendingUp size={14} /> +12%
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">{stats?.resolutionRate.rate}%</p>
                        <p className="text-sm text-slate-400">Resolution Rate</p>
                    </div>

                    <div className="glass-card p-6 border-l-4 border-violet-500">
                        <div className="flex items-center justify-between mb-4">
                            <span className="p-2 bg-violet-500/10 text-violet-400 rounded-lg">
                                <Clock size={20} />
                            </span>
                            <span className="text-xs font-medium text-danger-400 flex items-center gap-1">
                                <ArrowUpRight size={14} /> +5%
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">{stats?.averageResolutionDays || 0}d</p>
                        <p className="text-sm text-slate-400">Avg. Resolution Time</p>
                    </div>

                    <div className="glass-card p-6 border-l-4 border-warning-500">
                        <div className="flex items-center justify-between mb-4">
                            <span className="p-2 bg-warning-500/10 text-warning-400 rounded-lg">
                                <AlertTriangle size={20} />
                            </span>
                            <span className="text-xs font-medium text-success-400 flex items-center gap-1">
                                <ArrowDownRight size={14} /> -8%
                            </span>
                        </div>
                        <p className="text-2xl font-bold text-white">{stats?.overdueEscalations || 0}</p>
                        <p className="text-sm text-slate-400">Overdue Tasks</p>
                    </div>

                    <div className="glass-card p-6 border-l-4 border-success-500">
                        <div className="flex items-center justify-between mb-4">
                            <span className="p-2 bg-success-500/10 text-success-400 rounded-lg">
                                <BarChart3 size={20} />
                            </span>
                            <span className="text-xs font-medium text-primary-400">Stabilized</span>
                        </div>
                        <p className="text-2xl font-bold text-white">
                            {clientData?.clients.filter(c => c.riskScore > 0.7).length || 0}
                        </p>
                        <p className="text-sm text-slate-400">High Risk Clients</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Trend Chart */}
                    <div className="glass-card lg:col-span-2">
                        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                            <h3 className="font-semibold text-white flex items-center gap-2">
                                <Calendar size={18} className="text-primary-400" />
                                Escalation Peaks (Last 14 Days)
                            </h3>
                        </div>
                        <div className="p-6 h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={stats?.dailyTrends}>
                                    <defs>
                                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#64748b"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        stroke="#64748b"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                        allowDecimals={false}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
                                        itemStyle={{ color: '#818cf8' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="count"
                                        stroke="#6366f1"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorCount)"
                                        name="Escalations"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Resolution Rate Gauge */}
                    <div className="glass-card">
                        <div className="p-4 border-b border-slate-800">
                            <h3 className="font-semibold text-white">Resolution Distribution</h3>
                        </div>
                        <div className="p-6 h-[300px] flex items-center justify-center overflow-hidden">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={[
                                            { name: 'Resolved', value: stats?.resolutionRate.resolved || 0 },
                                            { name: 'Unresolved', value: stats?.resolutionRate.unresolved || 0 }
                                        ]}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        <Cell fill="#22c55e" />
                                        <Cell fill="#334155" />
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="absolute flex flex-col items-center">
                                <span className="text-2xl font-bold text-white">{stats?.resolutionRate.rate}%</span>
                                <span className="text-xs text-slate-500">Resolved</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Churn Risk Bar Chart */}
                    <div className="glass-card">
                        <div className="p-4 border-b border-slate-800">
                            <h3 className="font-semibold text-white">Top 5 Clients by Churn Risk</h3>
                        </div>
                        <div className="p-6 h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={churnData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                                    <XAxis type="number" hide />
                                    <YAxis
                                        dataKey="name"
                                        type="category"
                                        stroke="#64748b"
                                        fontSize={12}
                                        width={100}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <Tooltip
                                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
                                    />
                                    <Bar dataKey="risk" radius={[0, 4, 4, 0]} name="Risk %">
                                        {churnData.map((_entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Resolution Time Trend */}
                    <div className="glass-card">
                        <div className="p-4 border-b border-slate-800">
                            <h3 className="font-semibold text-white">Avg. Resolution Time (Hours)</h3>
                        </div>
                        <div className="p-6 h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={stats?.dailyTrends}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                                    <XAxis
                                        dataKey="date"
                                        stroke="#64748b"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        stroke="#64748b"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f1f5f9' }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="avgResolutionTime"
                                        stroke="#a855f7"
                                        strokeWidth={3}
                                        dot={{ r: 4, fill: '#a855f7', strokeWidth: 2, stroke: '#1e293b' }}
                                        activeDot={{ r: 6 }}
                                        name="Resolution hrs"
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Complaint Clusters Section */}
                <ComplaintClusters />
            </div>
        </div>
    );
}
