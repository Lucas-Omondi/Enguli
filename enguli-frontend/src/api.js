import axios from 'axios';

const rawBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
// Strip any trailing slash, then ensure it ends with /api
const sanitizedBase = rawBase.replace(/\/$/, '');
export const API_BASE_URL = sanitizedBase.endsWith('/api')
    ? sanitizedBase
    : `${sanitizedBase}/api`;

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json',
    }
});

api.interceptors.request.use(
    (config) => {
        // Adjust the key name if stored differently (e.g., 'access_token', 'token', or from auth store)
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    const res = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                        refresh: refreshToken,
                    });
                    const newAccess = res.data.access;
                    localStorage.setItem('access_token', newAccess);
                    originalRequest.headers.Authorization = `Bearer ${newAccess}`;
                    return api(originalRequest);
                } catch (refreshErr) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                    return Promise.reject(refreshErr);
                }
            }
        }
        return Promise.reject(error);
    }
);



export default {
    // Auth endpoints
    login(username, password) {
        return api.post('/api/auth/token/', { username, password });
    },
    getCurrentUser() {
        return api.get('/auth/me/');
    },

    // Stations
    getStations() {
        return api.get('/stations/');
    },
    createStation(stationData) {
        return api.post('/stations/', stationData);
    },

    // Sensors
    getSensors(stationId = null) {
        const params = stationId ? { station_id: stationId } : {};
        return api.get('/sensors/', { params });
    },
    createSensor(sensorData) {
        return api.post('/sensors/', sensorData);
    },
    getSensorReadings(stationId) {
        return apiClient.get('/api/telemetry/readings/', {
            params: { station_id: stationId }
        });
    },

    // Aggregates & Alerts
// Ensure it uses the exact name of your axios instance at the top of src/api.js (e.g., apiClient or api):
    getStationAnalytics(stationId) {
        return api.get(`/api/telemetry/readings/?station_id=${stationId}`);
    },
    getActiveAlerts() {
        return api.get('/alerts/', { params: { resolved: 'false' } });
    },

    // Telemetry Logs
    getTelemetryLogs(stationId = null) {
        const params = stationId ? { station_id: stationId } : {};
        return api.get('/telemetry/logs/', { params });
    },
    getUsers() {
        return api.get('/users/');
    },
    createUser(userData) {
        return api.post('/users/', userData);
    },
    getAlerts(params = {}) {
        return api.get('/alerts/', { params });
    },
    resolveAlert(alertId) {
        return api.post(`/alerts/${alertId}/resolve/`);
    },
    calculateStorageModel(params) {
        return api.post('/analytics/storage-model/', params);
    },
    exportTelemetryCSV(params = {}) {
        return api.get('/telemetry/export/csv/', {
            params,
            responseType: 'blob'
        });
    },

};