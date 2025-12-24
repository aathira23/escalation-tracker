/**
 * UI Store (Zustand)
 * Manages UI state like sidebar, modals, etc.
 */
import { create } from 'zustand';

interface UIState {
    sidebarOpen: boolean;
    activeModal: string | null;
    modalData: unknown;

    // Actions
    toggleSidebar: () => void;
    setSidebarOpen: (open: boolean) => void;
    openModal: (modalId: string, data?: unknown) => void;
    closeModal: () => void;
}

export const useUIStore = create<UIState>((set) => ({
    sidebarOpen: true,
    activeModal: null,
    modalData: null,

    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

    setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),

    openModal: (activeModal, modalData = null) => set({ activeModal, modalData }),

    closeModal: () => set({ activeModal: null, modalData: null }),
}));
