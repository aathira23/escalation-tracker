/**
 * Sidebar Component
 * Main navigation sidebar with role-based menu items
 */
import { NavLink, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    AlertTriangle,
    Building2,
    Users,
    BarChart3,
    LogOut,
    ChevronLeft,
    ChevronRight,
    Zap,
    Shield,
} from 'lucide-react';

import { useAuthStore } from '../../stores/authStore';
import { useUIStore } from '../../stores/uiStore';

interface NavItemProps {
    to: string;
    icon: React.ReactNode;
    label: string;
    collapsed?: boolean;
}

function NavItem({ to, icon, label, collapsed }: NavItemProps) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
            }
        >
            {icon}
            {!collapsed && <span>{label}</span>}
        </NavLink>
    );
}

export default function Sidebar() {
    const navigate = useNavigate();
    const { user, logout } = useAuthStore();
    const { sidebarOpen, toggleSidebar } = useUIStore();

    const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager';

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <aside
            className={`fixed left-0 top-0 h-full bg-slate-900 border-r border-slate-800 transition-all duration-300 z-40 flex flex-col ${sidebarOpen ? 'w-64' : 'w-20'
                }`}
        >
            {/* Header */}
            <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center flex-shrink-0">
                        <Zap className="w-5 h-5 text-white" />
                    </div>
                    {sidebarOpen && (
                        <span className="font-semibold text-white">Escalations</span>
                    )}
                </div>
                <button
                    onClick={toggleSidebar}
                    className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                >
                    {sidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
                <NavItem
                    to="/"
                    icon={<LayoutDashboard size={20} />}
                    label="Dashboard"
                    collapsed={!sidebarOpen}
                />
                <NavItem
                    to="/escalations"
                    icon={<AlertTriangle size={20} />}
                    label="Escalations"
                    collapsed={!sidebarOpen}
                />
                <NavItem
                    to="/clients"
                    icon={<Building2 size={20} />}
                    label="Clients"
                    collapsed={!sidebarOpen}
                />

                {isManagerOrAdmin && (
                    <>
                        <NavItem
                            to="/team"
                            icon={<Users size={20} />}
                            label="Team"
                            collapsed={!sidebarOpen}
                        />
                        <NavItem
                            to="/analytics"
                            icon={<BarChart3 size={20} />}
                            label="Analytics"
                            collapsed={!sidebarOpen}
                        />
                        {user.role === 'admin' && (
                            <NavItem
                                to="/settings"
                                icon={<Shield size={20} />}
                                label="System Admin"
                                collapsed={!sidebarOpen}
                            />
                        )}
                    </>
                )}
            </nav>

            {/* User section */}
            <div className="p-3 border-t border-slate-800">
                {sidebarOpen && user && (
                    <div className="mb-3 px-3">
                        <p className="text-sm font-medium text-white truncate">{user.fullName}</p>
                        <p className="text-xs text-slate-500 capitalize">{user.role}</p>
                    </div>
                )}
                <button
                    onClick={handleLogout}
                    className="nav-item w-full text-danger-500 hover:bg-danger-500/10"
                >
                    <LogOut size={20} />
                    {sidebarOpen && <span>Logout</span>}
                </button>
            </div>
        </aside>
    );
}
