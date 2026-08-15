import axios from 'axios';

// Dynamically use the Vercel environment variable in production,
// falling back to local Django development server when run locally
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000, // 15s timeout accounts for Render free-tier cold starts
    headers: {
        'Content-Type': 'application/json',
    }
});

export default {
    // Fetch all river monitoring stations
    getStations() {
        return api.get('/stations/');
    },

    // Fetch master sensor list or filter by station
    getSensors(stationId = null) {
        const params = stationId ? { station_id: stationId } : {};
        return api.get('/sensors/', { params });
    },

    // Get aggregated stats for the dashboard summary cards
    getStationAnalytics(stationId) {
        return api.get(`/analytics/stations/${stationId}/`);
    },

    // Fetch alerts flagged as active/unresolved
    getActiveAlerts() {
        return api.get('/alerts/', { params: { resolved: 'false' } });
    },

    // Fetch telemetry logs
    async getTelemetryLogs(stationId = null) {
        const params = stationId ? { station_id: stationId } : {};
        return api.get('/telemetry/logs/', { params });
    }
};