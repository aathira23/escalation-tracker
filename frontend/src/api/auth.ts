/**
 * Authentication API
 */
import apiClient from './client';
import type { AuthToken, LoginCredentials, User, UserCreate } from '../types';

export const authApi = {
    /**
     * Login with email and password
     */
    login: async (credentials: LoginCredentials): Promise<AuthToken> => {
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        const response = await apiClient.post<AuthToken>('/api/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },

    /**
     * Get current user info
     */
    getCurrentUser: async (): Promise<User> => {
        const response = await apiClient.get<User>('/api/auth/me');
        return response.data;
    },

    /**
     * Register new user (admin only)
     */
    register: async (userData: UserCreate): Promise<User> => {
        const response = await apiClient.post<User>('/api/auth/register', userData);
        return response.data;
    },

    /**
     * Setup initial admin (only works if no users exist)
     */
    setupAdmin: async (userData: UserCreate): Promise<User> => {
        const response = await apiClient.post<User>('/api/auth/setup-admin', userData);
        return response.data;
    },
};
