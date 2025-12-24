/**
 * Escalations API
 */
import apiClient from './client';
import type {
    Escalation,
    EscalationCreate,
    EscalationListResponse,
    EscalationFilters,
    EscalationAssign,
    EscalationStatusUpdate,
    TimelineEvent,
    Note,
    NoteCreate,
} from '../types';

export const escalationsApi = {
    /**
     * Get paginated list of escalations with optional filters
     */
    getAll: async (filters: EscalationFilters = {}): Promise<EscalationListResponse> => {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.priority) params.append('priority', filters.priority);
        if (filters.clientId) params.append('client_id', filters.clientId);
        if (filters.assignedTo) params.append('assigned_to', filters.assignedTo);
        if (filters.page) params.append('page', String(filters.page));
        if (filters.pageSize) params.append('page_size', String(filters.pageSize));

        const response = await apiClient.get<EscalationListResponse>('/api/escalations', { params });
        return response.data;
    },

    /**
     * Get single escalation by ID
     */
    getById: async (id: string): Promise<Escalation> => {
        const response = await apiClient.get<Escalation>(`/api/escalations/${id}`);
        return response.data;
    },

    /**
     * Create new escalation
     */
    create: async (data: EscalationCreate): Promise<Escalation> => {
        const response = await apiClient.post<Escalation>('/api/escalations', data);
        return response.data;
    },

    /**
     * Assign escalation to resolver
     */
    assign: async (id: string, data: EscalationAssign): Promise<Escalation> => {
        const response = await apiClient.post<Escalation>(`/api/escalations/${id}/assign`, data);
        return response.data;
    },

    /**
     * Update escalation status
     */
    updateStatus: async (id: string, data: EscalationStatusUpdate): Promise<Escalation> => {
        const response = await apiClient.put<Escalation>(`/api/escalations/${id}/status`, data);
        return response.data;
    },

    /**
     * Get escalation timeline
     */
    getTimeline: async (id: string): Promise<TimelineEvent[]> => {
        const response = await apiClient.get<TimelineEvent[]>(`/api/escalations/${id}/timeline`);
        return response.data;
    },

    /**
     * Get escalation notes
     */
    getNotes: async (id: string): Promise<Note[]> => {
        const response = await apiClient.get<Note[]>(`/api/escalations/${id}/notes`);
        return response.data;
    },

    /**
     * Add note to escalation
     */
    addNote: async (id: string, data: NoteCreate): Promise<Note> => {
        const response = await apiClient.post<Note>(`/api/escalations/${id}/notes`, data);
        return response.data;
    },
};
