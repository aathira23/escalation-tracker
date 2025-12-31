/**
 * Analytics API
 */
import apiClient from './client';
import type { DashboardStats, ClientAnalytics, TeamAnalytics, Insights, ComplaintCluster } from '../types';

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

    /**
     * Get AI-generated strategic insights
     */
    getAIInsights: async (): Promise<Insights> => {
        const response = await apiClient.get<Insights>('/api/analytics/insights');
        return response.data;
    },

    /**
     * Get AI-grouped complaint clusters
     */
    getClusters: async (): Promise<ComplaintCluster[]> => {
        const response = await apiClient.get<ComplaintCluster[]>('/api/analytics/clusters');
        return response.data;
    },
};
