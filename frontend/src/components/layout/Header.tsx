/**
 * Header Component
 * Top navigation bar with search and user info
 */
import { Bell, Search } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';

interface HeaderProps {
    title?: string;
}

export default function Header({ title }: HeaderProps) {
    const { user } = useAuthStore();

    return (
        <header className="h-16 bg-slate-900/50 backdrop-blur-xl border-b border-slate-800 flex items-center justify-between px-6">
            {/* Title */}
            <div>
                {title && <h1 className="text-xl font-semibold text-white">{title}</h1>}
            </div>

            {/* Right side */}
            <div className="flex items-center gap-4">
                {/* Search */}
                <div className="relative hidden md:block">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Search escalations..."
                        className="w-64 pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                </div>

                {/* Notifications */}
                <button className="relative p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
                    <Bell size={20} />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full" />
                </button>

                {/* User avatar */}
                {user && (
                    <div className="flex items-center gap-3 pl-3 border-l border-slate-700">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center">
                            <span className="text-sm font-medium text-white">
                                {user.fullName.charAt(0).toUpperCase()}
                            </span>
                        </div>
                        <div className="hidden md:block">
                            <p className="text-sm font-medium text-white">{user.fullName}</p>
                            <p className="text-xs text-slate-500 capitalize">{user.role}</p>
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
}
