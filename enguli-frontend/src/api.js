import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request Interceptor: Attach JWT Bearer Token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Handle Token Expiration (401)
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
                        refresh: refreshToken
                    });
                    const newAccessToken = res.data.access;
                    localStorage.setItem('access_token', newAccessToken);
                    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                    return api(originalRequest);
                } catch (refreshErr) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user_profile');
                    window.location.href = '/login';
                    return Promise.reject(refreshErr);
                }
            } else {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default {
    // Auth endpoints
    login(username, password) {
        return api.post('/auth/token/', { username, password });
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

    // Aggregates & Alerts
    getStationAnalytics(stationId) {
        return api.get(`/analytics/stations/${stationId}/`);
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
};