/**
 * Team Page
 * User management and workload overview
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    Users,
    UserPlus,
    Search,
    MoreVertical,
    Shield,
    Mail,
    Activity,
    X,
    Check
} from 'lucide-react';
import toast from 'react-hot-toast';

import Header from '../components/layout/Header';
import { usersApi } from '../api/users';
import { useAuthStore } from '../stores/authStore';

export default function TeamPage() {
    const { user: currentUser } = useAuthStore();
    const queryClient = useQueryClient();
    const isAdmin = currentUser?.role === 'admin';
    const isManager = currentUser?.role === 'manager';

    const [searchTerm, setSearchTerm] = useState('');
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [editingUser, setEditingUser] = useState<any>(null);
    const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

    const [newUser, setNewUser] = useState({
        email: '',
        fullName: '',
        password: '',
        role: 'viewer',
        maxConcurrentEscalations: 5,
        department_id: ''
    });

    // Fetch departments
    const { data: departments } = useQuery({
        queryKey: ['departments'],
        queryFn: () => usersApi.getDepartments(),
        enabled: isAdmin
    });

    // Fetch users
    const { data: users, isLoading } = useQuery({
        queryKey: ['users'],
        queryFn: () => usersApi.getAll(),
        enabled: isAdmin || isManager
    });

    // Add user mutation
    const addUserMutation = useMutation({
        mutationFn: usersApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            toast.success('User added successfully');
            setIsAddModalOpen(false);
            setNewUser({
                email: '',
                fullName: '',
                password: '',
                role: 'viewer',
                maxConcurrentEscalations: 5,
                department_id: ''
            });
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to add user');
        }
    });

    // Update user mutation
    const updateUserMutation = useMutation({
        mutationFn: ({ id, data }: { id: string, data: any }) => usersApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            toast.success('User updated successfully');
            setIsEditModalOpen(false);
            setEditingUser(null);
            setActiveDropdown(null);
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to update user');
        }
    });

    const filteredUsers = users?.filter(user =>
        user.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleAddUser = (e: React.FormEvent) => {
        e.preventDefault();
        addUserMutation.mutate(newUser);
    };

    const handleUpdateUser = (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingUser) return;

        const updateData = {
            full_name: editingUser.fullName,
            role: editingUser.role,
            department_id: editingUser.departmentId || null,
            max_concurrent_escalations: editingUser.maxConcurrentEscalations,
            is_active: editingUser.isActive
        };

        updateUserMutation.mutate({ id: editingUser.id, data: updateData });
    };

    const toggleUserStatus = (user: any) => {
        updateUserMutation.mutate({
            id: user.id,
            data: { is_active: !user.isActive }
        });
    };

    return (
        <div className="min-h-screen">
            <Header title="Team Management" />

            <div className="p-6 space-y-6">
                {/* Stats Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="glass-card p-6 flex items-center gap-4">
                        <div className="p-3 bg-primary-500/20 text-primary-400 rounded-lg">
                            <Users size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Total Members</p>
                            <p className="text-2xl font-bold text-white">{users?.length || 0}</p>
                        </div>
                    </div>
                    <div className="glass-card p-6 flex items-center gap-4">
                        <div className="p-3 bg-success-500/20 text-success-400 rounded-lg">
                            <Shield size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Admins/Managers</p>
                            <p className="text-2xl font-bold text-white">
                                {users?.filter(u => u.role !== 'viewer').length || 0}
                            </p>
                        </div>
                    </div>
                    <div className="glass-card p-6 flex items-center gap-4">
                        <div className="p-3 bg-violet-500/20 text-violet-400 rounded-lg">
                            <Activity size={24} />
                        </div>
                        <div>
                            <p className="text-sm text-slate-400">Active Resolvers</p>
                            <p className="text-2xl font-bold text-white">
                                {users?.filter(u => u.role === 'viewer' && u.isActive).length || 0}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Actions Bar */}
                <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                    <div className="relative w-full md:max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                        <input
                            type="text"
                            placeholder="Search by name or email..."
                            className="input-field pl-10"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    {isAdmin && (
                        <button
                            onClick={() => setIsAddModalOpen(true)}
                            className="btn-primary flex items-center gap-2 w-full md:w-auto"
                        >
                            <UserPlus size={18} />
                            Add User
                        </button>
                    )}
                </div>

                {/* Users Table */}
                <div className="glass-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-slate-800 bg-slate-800/20">
                                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">Name / Email</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">Role</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">Status</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">Workload</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">Projects</th>
                                    <th className="px-6 py-4 text-sm font-semibold text-slate-300 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {isLoading ? (
                                    [...Array(5)].map((_, i) => (
                                        <tr key={i} className="animate-pulse">
                                            <td colSpan={5} className="px-6 py-4">
                                                <div className="h-10 bg-slate-800/50 rounded" />
                                            </td>
                                        </tr>
                                    ))
                                ) : filteredUsers?.length ? (
                                    filteredUsers.map((user) => (
                                        <tr key={user.id} className="hover:bg-slate-800/30 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="font-medium text-white">{user.fullName}</div>
                                                <div className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                                                    <Mail size={12} /> {user.email}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${user.role === 'admin' ? 'bg-danger-500/10 text-danger-400 border-danger-500/20' :
                                                    user.role === 'manager' ? 'bg-warning-500/10 text-warning-400 border-warning-500/20' :
                                                        'bg-primary-500/10 text-primary-400 border-primary-500/20'
                                                    }`}>
                                                    {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-1.5">
                                                    <div className={`w-1.5 h-1.5 rounded-full ${user.isActive ? 'bg-success-500' : 'bg-slate-500'}`} />
                                                    <span className="text-sm">{user.isActive ? 'Active' : 'Inactive'}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="space-y-1.5">
                                                    <div className="flex justify-between text-xs">
                                                        <span className="text-slate-400">{user.currentEscalationCount} / {user.maxConcurrentEscalations} escalations</span>
                                                        <span className="font-medium">
                                                            {Math.round((user.currentEscalationCount / user.maxConcurrentEscalations) * 100)}%
                                                        </span>
                                                    </div>
                                                    <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full rounded-full ${(user.currentEscalationCount / user.maxConcurrentEscalations) >= 0.8 ? 'bg-danger-500' :
                                                                (user.currentEscalationCount / user.maxConcurrentEscalations) >= 0.5 ? 'bg-warning-500' :
                                                                    'bg-success-500'
                                                                }`}
                                                            style={{ width: `${Math.min((user.currentEscalationCount / user.maxConcurrentEscalations) * 100, 100)}%` }}
                                                        />
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex flex-wrap gap-1">
                                                    {(user as any).projectNames?.map((p: string, i: number) => (
                                                        <span key={i} className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700">
                                                            {p}
                                                        </span>
                                                    ))}
                                                    {(!(user as any).projectNames || (user as any).projectNames.length === 0) && (
                                                        <span className="text-[10px] text-slate-600 italic">No Projects</span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="relative inline-block text-left">
                                                    <button
                                                        onClick={() => setActiveDropdown(activeDropdown === user.id ? null : user.id)}
                                                        className="text-slate-500 hover:text-white transition-colors"
                                                    >
                                                        <MoreVertical size={18} />
                                                    </button>

                                                    {activeDropdown === user.id && (isAdmin || isManager) && (
                                                        <>
                                                            <div className="fixed inset-0 z-10" onClick={() => setActiveDropdown(null)} />
                                                            <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-slate-900 ring-1 ring-black ring-opacity-5 z-20 border border-slate-800">
                                                                <div className="py-1" role="menu" aria-orientation="vertical">
                                                                    <button
                                                                        onClick={() => {
                                                                            setEditingUser({ ...user });
                                                                            setIsEditModalOpen(true);
                                                                            setActiveDropdown(null);
                                                                        }}
                                                                        className="flex w-full items-center px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-white"
                                                                        role="menuitem"
                                                                    >
                                                                        Edit Details
                                                                    </button>
                                                                    <button
                                                                        onClick={() => toggleUserStatus(user)}
                                                                        className={`flex w-full items-center px-4 py-2 text-sm ${user.isActive ? 'text-danger-400' : 'text-success-400'} hover:bg-slate-800`}
                                                                        role="menuitem"
                                                                    >
                                                                        {user.isActive ? 'Deactivate User' : 'Activate User'}
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        </>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                                            No team members found
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Add User Modal */}
            {isAddModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={() => setIsAddModalOpen(false)} />
                    <div className="relative glass-card w-full max-w-md p-6 shadow-2xl">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <UserPlus className="text-primary-400" /> Add New User
                            </h3>
                            <button onClick={() => setIsAddModalOpen(false)} className="text-slate-400 hover:text-white">
                                <X size={20} />
                            </button>
                        </div>

                        <form onSubmit={handleAddUser} className="space-y-4">
                            <div>
                                <label className="input-label">Full Name</label>
                                <input
                                    type="text"
                                    required
                                    className="input-field"
                                    placeholder="John Doe"
                                    value={newUser.fullName}
                                    onChange={(e) => setNewUser({ ...newUser, fullName: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="input-label">Email Address</label>
                                <input
                                    type="email"
                                    required
                                    className="input-field"
                                    placeholder="john@company.com"
                                    value={newUser.email}
                                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="input-label">Initial Password</label>
                                <input
                                    type="password"
                                    required
                                    className="input-field"
                                    placeholder="••••••••"
                                    value={newUser.password}
                                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="input-label">Role</label>
                                    <select
                                        className="input-field"
                                        value={newUser.role}
                                        onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                                    >
                                        <option value="viewer">Viewer (Resolver)</option>
                                        <option value="manager">Manager</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="input-label">Department</label>
                                    <select
                                        className="input-field"
                                        value={newUser.department_id}
                                        onChange={(e) => setNewUser({ ...newUser, department_id: e.target.value })}
                                    >
                                        <option value="">No Department</option>
                                        {departments?.map((d: any) => (
                                            <option key={d.id} value={d.id}>{d.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="input-label">Max Capacity</label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="20"
                                        className="input-field"
                                        value={newUser.maxConcurrentEscalations}
                                        onChange={(e) => setNewUser({ ...newUser, maxConcurrentEscalations: parseInt(e.target.value) })}
                                    />
                                </div>
                            </div>

                            <div className="pt-4 flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setIsAddModalOpen(false)}
                                    className="btn-secondary flex-1"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={addUserMutation.isPending}
                                    className="btn-primary flex-1 flex items-center justify-center gap-2"
                                >
                                    {addUserMutation.isPending ? (
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    ) : (
                                        <>
                                            <Check size={18} /> Create User
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Edit User Modal */}
            {isEditModalOpen && editingUser && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={() => setIsEditModalOpen(false)} />
                    <div className="relative glass-card w-full max-w-md p-6 shadow-2xl">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <Activity className="text-primary-400" /> Edit User
                            </h3>
                            <button onClick={() => setIsEditModalOpen(false)} className="text-slate-400 hover:text-white">
                                <X size={20} />
                            </button>
                        </div>

                        <form onSubmit={handleUpdateUser} className="space-y-4">
                            <div>
                                <label className="input-label">Full Name</label>
                                <input
                                    type="text"
                                    required
                                    className="input-field"
                                    value={editingUser.fullName}
                                    onChange={(e) => setEditingUser({ ...editingUser, fullName: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="input-label">Email Address (Read Only)</label>
                                <input
                                    type="email"
                                    disabled
                                    className="input-field opacity-60 cursor-not-allowed"
                                    value={editingUser.email}
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="input-label">Role</label>
                                    <select
                                        className={`input-field ${!isAdmin ? 'opacity-60 cursor-not-allowed' : ''}`}
                                        disabled={!isAdmin}
                                        value={editingUser.role}
                                        onChange={(e) => setEditingUser({ ...editingUser, role: e.target.value })}
                                    >
                                        <option value="viewer">Viewer (Resolver)</option>
                                        <option value="manager">Manager</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="input-label">Department</label>
                                    <select
                                        className={`input-field ${!isAdmin ? 'opacity-60 cursor-not-allowed' : ''}`}
                                        disabled={!isAdmin}
                                        value={editingUser.departmentId || ''}
                                        onChange={(e) => setEditingUser({ ...editingUser, departmentId: e.target.value })}
                                    >
                                        <option value="">No Department</option>
                                        {departments?.map((d: any) => (
                                            <option key={d.id} value={d.id}>{d.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="input-label">Max Capacity</label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="20"
                                        className="input-field"
                                        value={editingUser.maxConcurrentEscalations}
                                        onChange={(e) => setEditingUser({ ...editingUser, maxConcurrentEscalations: parseInt(e.target.value) })}
                                    />
                                </div>
                                <div className="flex items-end pb-1">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-primary-500 focus:ring-primary-500"
                                            checked={editingUser.isActive}
                                            onChange={(e) => setEditingUser({ ...editingUser, isActive: e.target.checked })}
                                        />
                                        <span className="text-sm text-slate-300">Account Active</span>
                                    </label>
                                </div>
                            </div>

                            <div className="pt-4 flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setIsEditModalOpen(false)}
                                    className="btn-secondary flex-1"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={updateUserMutation.isPending}
                                    className="btn-primary flex-1 flex items-center justify-center gap-2"
                                >
                                    {updateUserMutation.isPending ? (
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    ) : (
                                        <>
                                            <Check size={18} /> Save Changes
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
