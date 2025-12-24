/**
 * Analytics API
 */
import apiClient from './client';
import type { DashboardStats, ClientAnalytics, TeamAnalytics } from '../types';

export const analyticsApi = {
    /**
     * Get dashboard overview stats
     */
    getDashboardStats: async (): Promise<DashboardStats> => {
        const response = await apiClient.get<DashboardStats>('/api/analytics/overview');
        return response.data;
    },

    /**
     * Get client analytics
     */
    getClientAnalytics: async (): Promise<ClientAnalytics> => {
        const response = await apiClient.get<ClientAnalytics>('/api/analytics/clients');
        return response.data;
    },

    /**
     * Get team performance analytics
     */
    getTeamAnalytics: async (): Promise<TeamAnalytics> => {
        const response = await apiClient.get<TeamAnalytics>('/api/analytics/team');
        return response.data;
    },
};
