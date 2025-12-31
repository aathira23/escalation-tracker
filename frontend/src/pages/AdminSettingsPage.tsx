import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Building,
    Shield,
    CheckCircle,
    XCircle,
    Search,
} from 'lucide-react';
import toast from 'react-hot-toast';

import Header from '../components/layout/Header';
import { usersApi } from '../api/users';
import { useAuthStore } from '../stores/authStore';

export default function AdminSettingsPage() {
    const { user: currentUser } = useAuthStore();
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [roleFilter, setRoleFilter] = useState<string>('');
    const [editingUser, setEditingUser] = useState<string | null>(null);

    // Fetch all users
    const { data: users } = useQuery({
        queryKey: ['admin-users'],
        queryFn: () => usersApi.getAll(undefined, true),
        enabled: currentUser?.role === 'admin'
    });

    // Fetch departments
    const { data: departments } = useQuery({
        queryKey: ['departments'],
        queryFn: () => usersApi.getDepartments(),
        enabled: !!currentUser
    });

    // Mutation for updating user
    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string, data: any }) =>
            usersApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-users'] });
            setEditingUser(null);
            toast.success('User updated successfully');
        },
        onError: () => {
            toast.error('Failed to update user');
        }
    });

    if (currentUser?.role !== 'admin') {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400">
                <Shield size={48} className="mb-4 text-slate-600" />
                <h1 className="text-xl font-bold text-white">Access Restricted</h1>
                <p>Only administrators can access this page.</p>
            </div>
        );
    }

    const filteredUsers = users?.filter(u => {
        const matchesSearch = u.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
            u.email.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesRole = roleFilter === '' || u.role === roleFilter;
        return matchesSearch && matchesRole;
    });

    return (
        <div className="min-h-screen">
            <Header title="System Administration" />

            <div className="p-6 max-w-7xl mx-auto space-y-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-white mb-1">User & Organizational Mapping</h1>
                        <p className="text-slate-400 text-sm">Manage user assignments to departments and projects.</p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        <div className="relative">
                            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search users..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="input-field pl-10 py-2 text-sm w-64"
                            />
                        </div>
                        <select
                            value={roleFilter}
                            onChange={(e) => setRoleFilter(e.target.value)}
                            className="input-field py-2 text-sm"
                        >
                            <option value="">All Roles</option>
                            <option value="admin">Admins</option>
                            <option value="manager">Managers</option>
                            <option value="viewer">Moderators (Viewers)</option>
                        </select>
                    </div>
                </div>

                <div className="glass-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-800/50 text-slate-400 text-[10px] font-bold uppercase tracking-widest border-b border-slate-700">
                                    <th className="px-6 py-4">User</th>
                                    <th className="px-6 py-4">Role</th>
                                    <th className="px-6 py-4">Department</th>
                                    <th className="px-6 py-4">Status</th>
                                    <th className="px-6 py-4">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {filteredUsers?.map((u) => (
                                    <tr key={u.id} className="hover:bg-slate-800/30 transition-colors group">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 font-bold border border-slate-600">
                                                    {u.fullName.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="text-white font-medium">{u.fullName}</div>
                                                    <div className="text-xs text-slate-500">{u.email}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-tight ${u.role === 'admin' ? 'bg-danger-500/10 text-danger-400 border border-danger-500/20' :
                                                    u.role === 'manager' ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20' :
                                                        'bg-slate-700/50 text-slate-400 border border-slate-600'
                                                }`}>
                                                {u.role}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            {editingUser === u.id ? (
                                                <select
                                                    className="input-field py-1 text-xs"
                                                    value={u.departmentId || ''}
                                                    onChange={(e) => updateMutation.mutate({
                                                        id: u.id,
                                                        data: { department_id: e.target.value || null }
                                                    })}
                                                >
                                                    <option value="">No Department</option>
                                                    {departments?.map((d: any) => (
                                                        <option key={d.id} value={d.id}>{d.name}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                <div className="flex items-center gap-2">
                                                    <Building size={14} className="text-slate-500" />
                                                    <span className="text-slate-300 text-sm">
                                                        {u.departmentName || <span className="text-slate-600 italic">Not Mapped</span>}
                                                    </span>
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-1.5">
                                                {u.isActive ? (
                                                    <><CheckCircle size={14} className="text-success-500" /><span className="text-xs text-success-500 font-medium">Active</span></>
                                                ) : (
                                                    <><XCircle size={14} className="text-slate-500" /><span className="text-xs text-slate-500 font-medium">Disabled</span></>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => setEditingUser(editingUser === u.id ? null : u.id)}
                                                className="text-primary-400 hover:text-primary-300 text-xs font-semibold"
                                            >
                                                {editingUser === u.id ? 'Cancel' : 'Edit Mapping'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {filteredUsers?.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="px-6 py-10 text-center text-slate-500 italic">
                                            No users found matching your criteria.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
