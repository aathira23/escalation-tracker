/**
 * Main Layout Component
 * Wraps authenticated pages with sidebar and header
 */
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useUIStore } from '../../stores/uiStore';
import { useWebSockets } from '../../hooks/useWebSockets';

export default function Layout() {
    const { sidebarOpen } = useUIStore();
    useWebSockets();

    return (
        <div className="min-h-screen bg-slate-950">
            <Sidebar />
            <main
                className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'
                    }`}
            >
                <Outlet />
            </main>
        </div>
    );
}
