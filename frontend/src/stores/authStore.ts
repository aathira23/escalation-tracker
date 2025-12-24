/**
 * Authentication Store (Zustand)
 * Manages user session state with persistence
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types';

interface AuthState {
    token: string | null;
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;

    // Actions
    setToken: (token: string) => void;
    setUser: (user: User) => void;
    logout: () => void;
    setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            token: null,
            user: null,
            isAuthenticated: false,
            isLoading: false,

            setToken: (token) => set({ token, isAuthenticated: true }),

            setUser: (user) => set({ user }),

            logout: () => set({ token: null, user: null, isAuthenticated: false }),

            setLoading: (isLoading) => set({ isLoading }),
        }),
        {
            name: 'auth-storage', // localStorage key
            partialize: (state) => ({ token: state.token }), // Only persist token
        }
    )
);
