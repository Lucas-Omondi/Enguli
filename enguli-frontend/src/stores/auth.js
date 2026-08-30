import { defineStore } from 'pinia';
import axios from 'axios';

const rawBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
// Strip any trailing slash, then ensure it ends with /api
const sanitizedBase = rawBase.replace(/\/$/, '');
export const API_BASE_URL = sanitizedBase.endsWith('/api')
    ? sanitizedBase
    : `${sanitizedBase}/api`;

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('access_token') || null,
        refreshToken: localStorage.getItem('refresh_token') || null,
        user: JSON.parse(localStorage.getItem('user_profile') || 'null'),
        isLoading: false,
        authError: null
    }),

    getters: {
        isAuthenticated: (state) => !!state.accessToken,

        // Resolve user role with safe fallbacks
        userRole: (state) => {
            if (state.user?.is_superuser) return 'ADMIN';
            return state.user?.profile?.role || 'OBSERVER';
        },

        roleDisplayName: (state) => {
            const role = state.user?.is_superuser ? 'ADMIN' : (state.user?.profile?.role || 'OBSERVER');
            if (role === 'ADMIN') return 'System Administrator';
            if (role === 'FIELD_ENGINEER') return 'Field Engineer';
            return 'Farmer / Observer';
        },

        // Grant management rights to Admins, Field Engineers, and superusers
        canManageHardware: (state) => {
            if (state.user?.is_superuser) return true;
            const role = state.user?.profile?.role;
            return role === 'ADMIN' || role === 'FIELD_ENGINEER';
        }
    },

    actions: {
        async login(username, password) {
            this.isLoading = true;
            this.authError = null;

            try {
                const response = await axios.post(`${API_BASE_URL}/auth/token/`, {
                    username,
                    password
                });

                this.accessToken = response.data.access;
                this.refreshToken = response.data.refresh;

                localStorage.setItem('access_token', this.accessToken);
                localStorage.setItem('refresh_token', this.refreshToken);

                // Await profile fetch BEFORE finishing login
                await this.fetchCurrentUser();
                return true;
            } catch (error) {
                this.authError = error.response?.data?.detail || 'Invalid username or password.';
                throw error;
            } finally {
                this.isLoading = false;
            }
        },

        async fetchCurrentUser() {
            if (!this.accessToken) return;
            try {
                const response = await axios.get(`${API_BASE_URL}/auth/me/`, {
                    headers: { Authorization: `Bearer ${this.accessToken}` }
                });
                this.user = response.data;
                localStorage.setItem('user_profile', JSON.stringify(this.user));
            } catch (error) {
                console.error('Failed to fetch user profile:', error);
            }
        },

        logout() {
            this.accessToken = null;
            this.refreshToken = null;
            this.user = null;
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_profile');
        }
    }
});