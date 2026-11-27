import { ref, onMounted, onUnmounted } from 'vue'
import api from '../api'

export function formatMetricLength(valueInMeters, decimalsCm = 1, decimalsM = 2) {
    if (valueInMeters === null || valueInMeters === undefined || Number.isNaN(Number(valueInMeters))) {
        return '--'
    }
    const num = Number(valueInMeters)
    if (Math.abs(num) < 1) {
        return `${(num * 100).toFixed(decimalsCm)} cm`
    }
    return `${num.toFixed(decimalsM)} m`
}

export function useStationStatus(pollIntervalMs = 15000) {
    const stations = ref([])
    const now = ref(Date.now())
    const loading = ref(false)
    let pollTimer = null
    let clockTimer = null

    const fetchStations = async () => {
        try {
            const res = await api.getStations()
            const data = res.data
            stations.value = data?.results || (Array.isArray(data) ? data : [])
        } catch (err) {
            console.error('[StationStatus] Failed to fetch stations:', err)
        }
    }

    // Evaluates live status using last_seen + offline_threshold_seconds (default 75s)
    const isStationOnline = (station) => {
        if (!station || !station.last_seen) return false
        const lastSeenMs = new Date(station.last_seen).getTime()
        const thresholdMs = (station.offline_threshold_seconds || 75) * 1000
        return (now.value - lastSeenMs) <= thresholdMs
    }

    const getStationStatusLabel = (station) => {
        return isStationOnline(station) ? 'ONLINE' : 'UNAVAILABLE'
    }

    const formatLastSeen = (lastSeen) => {
        if (!lastSeen) return 'Never connected'
        const diffSec = Math.max(0, Math.floor((now.value - new Date(lastSeen).getTime()) / 1000))
        if (diffSec < 60) return `${diffSec}s ago`
        if (diffSec < 3600) {
            const mins = Math.floor(diffSec / 60)
            const secs = diffSec % 60
            return `${mins}m ${secs}s ago`
        }
        return new Date(lastSeen).toLocaleString()
    }

    onMounted(async () => {
        now.value = Date.now()
        loading.value = true
        await fetchStations()
        loading.value = false

        pollTimer = setInterval(fetchStations, pollIntervalMs)
        clockTimer = setInterval(() => {
            now.value = Date.now()
        }, 1000)
    })

    onUnmounted(() => {
        if (pollTimer) clearInterval(pollTimer)
        if (clockTimer) clearInterval(clockTimer)
    })

    return {
        stations,
        loading,
        fetchStations,
        isStationOnline,
        getStationStatusLabel,
        formatLastSeen,
        formatMetricLength,
    }
}