/**
 * Filter Store (Zustand)
 * Manages escalation filter state
 */
import { create } from 'zustand';
import type { EscalationFilters } from '../types';

interface FilterState {
    filters: EscalationFilters;

    // Actions
    setFilter: <K extends keyof EscalationFilters>(key: K, value: EscalationFilters[K]) => void;
    resetFilters: () => void;
    setPage: (page: number) => void;
}

const defaultFilters: EscalationFilters = {
    page: 1,
    pageSize: 20,
};

export const useFilterStore = create<FilterState>((set) => ({
    filters: defaultFilters,

    setFilter: (key, value) =>
        set((state) => ({
            filters: { ...state.filters, [key]: value, page: 1 }, // Reset page on filter change
        })),

    resetFilters: () => set({ filters: defaultFilters }),

    setPage: (page) => set((state) => ({ filters: { ...state.filters, page } })),
}));
