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

// Request Interceptor: Attach JWT Bearer token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Refresh token on 401
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
    // Auth endpoints (fixed: removed redundant /api)
    login(username, password) {
        return api.post('/auth/token/', { username, password });
    },
    getCurrentUser() {
        return api.get('/auth/me/');
    },

    // Stations
    getStations() {
        // If your Django route is /api/stations/stations/, change to '/stations/stations/'
        return api.get('/stations/');
    },
    createStation(stationData) {
        return api.post('/stations/', stationData);
    },

    // Sensors
    getSensors(stationId = null) {
        const params = stationId ? { station_id: stationId } : {};
        return api.get('/sensors/sensors/', { params });
    },
    createSensor(sensorData) {
        return api.post('/sensors/sensors/', sensorData);
    },
    getSensorReadings(stationId) {
        // fixed: changed apiClient to api
        return api.get('/telemetry/logs/', {
            params: { station_id: stationId }
        });
    },

    // Aggregates & Alerts
    getStationAnalytics(stationId) {
        return api.get('/telemetry/logs/', {
            params: { station_id: stationId }
        });
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