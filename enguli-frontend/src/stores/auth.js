import { defineStore } from 'pinia';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

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
        userRole: (state) => state.user?.profile?.role || 'OBSERVER',
        // Display names mapping
        roleDisplayName: (state) => {
            const role = state.user?.profile?.role;
            if (role === 'ADMIN') return 'System Administrator';
            if (role === 'FIELD_ENGINEER') return 'Field Engineer';
            return 'Farmer';
        },
        canManageHardware: (state) => {
            const role = state.user?.profile?.role;
            return role === 'ADMIN' || role === 'FIELD_ENGINEER' || state.user?.is_superuser;
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

                // Fetch user profile & role
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