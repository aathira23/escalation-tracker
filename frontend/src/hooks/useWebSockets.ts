import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { useAuthStore } from '../stores/authStore';

export const useWebSockets = () => {
    const { token, user } = useAuthStore();
    const queryClient = useQueryClient();

    useEffect(() => {
        if (!token) return;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws?token=${token}`;
        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);

            // Global notifications
            if (message.type === 'escalation_assigned' && message.assignee_id === user?.id) {
                toast(`New escalation assigned to you: ${message.escalation_id}`, {
                    icon: '👤',
                    duration: 5000,
                });
                queryClient.invalidateQueries({ queryKey: ['escalations'] });
            }

            if (message.type === 'escalation_status_updated') {
                // Invalidate any list or item queries
                queryClient.invalidateQueries({ queryKey: ['escalations'] });
                queryClient.invalidateQueries({ queryKey: ['escalation', message.escalation_id] });
                queryClient.invalidateQueries({ queryKey: ['timeline', message.escalation_id] });
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
        };

        return () => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
        };
    }, [token, user?.id, queryClient]);
};
