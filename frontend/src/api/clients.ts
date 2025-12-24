/**
 * Clients API
 */
import apiClient from './client';
import type { Client, ClientCreate } from '../types';

export const clientsApi = {
    /**
     * Get all clients
     */
    getAll: async (): Promise<Client[]> => {
        const response = await apiClient.get<Client[]>('/api/clients');
        return response.data;
    },

    /**
     * Get client by ID
     */
    getById: async (id: string): Promise<Client> => {
        const response = await apiClient.get<Client>(`/api/clients/${id}`);
        return response.data;
    },

    /**
     * Create new client
     */
    create: async (data: ClientCreate): Promise<Client> => {
        const response = await apiClient.post<Client>('/api/clients', data);
        return response.data;
    },

    /**
     * Update client
     */
    update: async (id: string, data: Partial<ClientCreate>): Promise<Client> => {
        const response = await apiClient.put<Client>(`/api/clients/${id}`, data);
        return response.data;
    },

    /**
     * Delete client
     */
    delete: async (id: string): Promise<void> => {
        await apiClient.delete(`/api/clients/${id}`);
    },
};
