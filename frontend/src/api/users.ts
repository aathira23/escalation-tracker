/**
 * Users API
 */
import apiClient from './client';
import type { User } from '../types';

export const usersApi = {
    /**
     * Get all users
     */
    getAll: async (role?: string, includeInactive = false): Promise<User[]> => {
        const params = new URLSearchParams();
        if (role) params.append('role', role);
        if (includeInactive) params.append('include_inactive', 'true');

        const response = await apiClient.get<User[]>('/api/users', { params });
        return response.data;
    },

    /**
     * Get user by ID
     */
    getById: async (id: string): Promise<User> => {
        const response = await apiClient.get<User>(`/api/users/${id}`);
        return response.data;
    },

    /**
     * Get available resolvers (viewers with capacity)
     */
    getAvailableResolvers: async (): Promise<User[]> => {
        const response = await apiClient.get<User[]>('/api/users/resolvers/available');
        return response.data;
    },

    /**
     * Create a new user (admin only)
     */
    create: async (userData: any): Promise<User> => {
        const response = await apiClient.post<User>('/api/users', userData);
        return response.data;
    },

    /**
     * Update user details
     */
    update: async (id: string, userData: any): Promise<User> => {
        const response = await apiClient.put<User>(`/api/users/${id}`, userData);
        return response.data;
    },

    /**
     * Get all departments
     */
    getDepartments: async (): Promise<any[]> => {
        const response = await apiClient.get<any[]>('/api/departments');
        return response.data;
    },
};
