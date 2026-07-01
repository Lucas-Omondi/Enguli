import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    timeout: 10000,
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
        return api.get('/sensors/', { params }); // Handles tracking master diagnostics
    },

    // Get aggregated stats for the dashboard summary cards
    getStationAnalytics(stationId) {
        // Appended trailing slash to match typical Django route processing safely
        return api.get(`/analytics/stations/${stationId}/`);
    },

    // Fetch alerts flagged as active/unresolved
    getActiveAlerts() {
        // Updated path from '/alerts/alerts/' to '/alerts/' to match your router inclusion
        return api.get('/alerts/', { params: { resolved: 'false' } });
    },
    async getTelemetryLogs(stationId = null) {
        let url = '/telemetry/logs/';
        if (stationId) {
            url += `?station_id=${stationId}`;
        }
        return api.get(url);
    }
};