<template>
  <div class="analytics-wrapper">

    <!-- Header Section -->
    <div class="analytics-header">
      <div>
        <h1 class="analytics-title">Hydrological Analytics</h1>
        <p class="analytics-subtitle">Time-series aquifer dynamics and abstraction tracking parameters.</p>
      </div>
    </div>

    <!-- Controls Bar -->
    <div class="analytics-controls">
      <div class="control-group">
        <label class="control-label">Monitored Station Node</label>
        <select
            v-model="selectedStationId"
            @change="handleStationChange"
            class="station-dropdown-select"
        >
          <option v-for="station in stations" :key="station.id" :value="station.id">
            {{ station.station_code }} - {{ station.station_name }}
          </option>
        </select>
      </div>

      <!-- Real-Time Node Connectivity Status -->
      <div v-if="activeStation" class="node-status-panel">
        <span
            class="status-badge"
            :class="isStationOnline(activeStation) ? 'status-online' : 'status-unavailable'"
        >
          <span class="status-dot"></span>
          {{ getStationStatusLabel(activeStation) }}
        </span>
        <span class="last-heartbeat-text">
          Last ping: {{ formatLastSeen(activeStation.last_seen) }}
        </span>
      </div>
    </div>

    <!-- Stats Summary Strip (2-col on mobile, 4-col on desktop) -->
    <div class="stats-summary-strip">
      <div class="stat-box-mini">
        <span class="stat-box-label">Station ID Code</span>
        <span class="stat-box-value">{{ activeStationDetails.code }}</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Average Water Table</span>
        <span class="stat-box-value">{{ formatMetricLength(metrics.avg) }}</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Historical Min (Drawdown)</span>
        <span class="stat-box-value text-amber">{{ formatMetricLength(metrics.min) }}</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Historical Max (Recharge)</span>
        <span class="stat-box-value text-sage">{{ formatMetricLength(metrics.max) }}</span>
      </div>
    </div>

    <!-- Chart Card -->
    <div class="chart-card-container">
      <div class="chart-title-bar">
        <h3 class="chart-title-text">
          <i class="pi pi-chart-line text-sage"></i>
          Groundwater Level Fluctuations & Safety Limits
        </h3>
        <span class="chart-tag-text">Live Ingested Telemetry (H - D)</span>
      </div>

      <div class="chart-canvas-box" v-if="loaded && chartData.labels.length > 0">
        <Line :data="chartData" :options="chartOptions" />
      </div>

      <!-- Empty State -->
      <div class="chart-empty-box" v-else-if="loaded && chartData.labels.length === 0">
        <i class="pi pi-database text-stone-400 text-3xl"></i>
        <p class="empty-heading">No Telemetry Recorded Yet</p>
        <p class="empty-msg">Waiting for initial transmission from station sensors.</p>
      </div>

      <!-- Loading State -->
      <div class="chart-loading-box" v-else>
        <i class="pi pi-spin pi-spinner text-sage text-2xl"></i>
        <p class="loading-msg">Querying aquifer histories...</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
  Filler
} from 'chart.js';
import api from "../api";
import { useStationStatus, formatMetricLength } from "../composables/useStationStatus";

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, Filler);

// Live polling composable (polls /api/stations/ every 15s + 1s local clock check)
const {
  stations,
  loading: stationsLoading,
  isStationOnline,
  getStationStatusLabel,
  formatLastSeen
} = useStationStatus(15000);

const loaded = ref(false);
const selectedStationId = ref(null);
const metrics = ref({ avg: null, min: null, max: null });
const chartData = ref({ labels: [], datasets: [] });
const chartOptions = ref({});

let telemetryRefreshTimer = null;

// Dynamically binds to the live-polled station object
const activeStation = computed(() => {
  return stations.value.find(s => s.id === selectedStationId.value) || null;
});

const activeStationDetails = computed(() => {
  return {
    code: activeStation.value?.station_code || '---'
  };
});

// Automatically select the first station once useStationStatus loads
watch(
    stations,
    async (newStations) => {
      if (newStations.length > 0 && !selectedStationId.value) {
        selectedStationId.value = newStations[0].id;
        await fetchStationData(selectedStationId.value);
      } else if (!stationsLoading.value && newStations.length === 0) {
        loaded.value = true;
      }
    },
    { immediate: true }
);

const fetchStationData = async (stationId, silent = false) => {
  if (!silent) loaded.value = false;
  try {
    // Uses centralized api client which manages baseURL and auth headers
    const res = await api.getStationAnalytics(stationId);
    const data = res.data;
    const logs = data?.results || (Array.isArray(data) ? data : []);

    if (logs.length > 0) {
      // Chronological progression for left-to-right plotting
      const chronologicalLogs = [...logs].reverse();

      const timelineLabels = [];
      const waterLevelValues = [];
      let total = 0;
      let minVal = Infinity;
      let maxVal = -Infinity;

      chronologicalLogs.forEach((entry) => {
        if (entry.water_level !== null && entry.water_level !== undefined) {
          const val = Number(entry.water_level);
          if (!Number.isNaN(val)) {
            waterLevelValues.push(Number(val.toFixed(4)));

            total += val;
            if (val < minVal) minVal = val;
            if (val > maxVal) maxVal = val;

            if (entry.timestamp) {
              const date = new Date(entry.timestamp);
              const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
              timelineLabels.push(timeStr);
            } else {
              timelineLabels.push(`Log #${entry.id}`);
            }
          }
        }
      });

      const count = waterLevelValues.length;
      if (count > 0) {
        metrics.value = {
          avg: total / count,
          min: minVal,
          max: maxVal
        };
      } else {
        metrics.value = { avg: null, min: null, max: null };
      }

      setupChartEngine(timelineLabels, waterLevelValues);
    } else {
      metrics.value = { avg: null, min: null, max: null };
      setupChartEngine([], []);
    }

    loaded.value = true;
  } catch (error) {
    console.error("Error querying station telemetry parameters:", error);
    if (!silent) {
      metrics.value = { avg: null, min: null, max: null };
      setupChartEngine([], []);
    }
    loaded.value = true;
  }
};

const handleStationChange = () => {
  if (selectedStationId.value) {
    fetchStationData(selectedStationId.value);
  }
};

const setupChartEngine = (labels, values) => {
  chartData.value = {
    labels: labels,
    datasets: [
      {
        label: 'Calibrated Water Table Depth',
        data: values,
        borderColor: '#52796f',
        borderWidth: 2,
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return null;

          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(82, 121, 111, 0.20)');
          gradient.addColorStop(1, 'rgba(82, 121, 111, 0.00)');
          return gradient;
        },
        fill: true,
        tension: 0.3,
        pointBackgroundColor: '#52796f',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 1.5,
        pointHoverRadius: 6,
        pointRadius: values.length > 50 ? 0 : 3.5
      }
    ]
  };

  chartOptions.value = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#383533',
        titleColor: '#f7f6f4',
        bodyColor: '#e7e4df',
        titleFont: { size: 11, weight: '600' },
        bodyFont: { size: 12 },
        padding: 8,
        cornerRadius: 6,
        displayColors: false,
        callbacks: {
          label: (context) => ` Water Level: ${formatMetricLength(context.parsed.y)}`
        }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: {
          color: '#8c857b',
          font: { size: 10 },
          maxRotation: 45,
          minRotation: 0
        }
      },
      y: {
        suggestedMin: 0,
        suggestedMax: 0.4,
        ticks: {
          color: '#8c857b',
          font: { size: 10 },
          callback: (value) => formatMetricLength(value, 0, 2)
        },
        grid: { color: '#ece8e1' }
      }
    }
  };
};

onMounted(() => {
  // Silently refresh chart data every 30s so new telemetry points appear live
  telemetryRefreshTimer = setInterval(() => {
    if (selectedStationId.value) {
      fetchStationData(selectedStationId.value, true);
    }
  }, 30000);
});

onUnmounted(() => {
  if (telemetryRefreshTimer) clearInterval(telemetryRefreshTimer);
});
</script>

<style scoped>
/* Main Page Layout */
.analytics-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
}

.analytics-header {
  margin-bottom: 0.15rem;
}

.analytics-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.02em;
  margin: 0;
}

.analytics-subtitle {
  font-size: 0.825rem;
  color: #78716c;
  margin: 0.25rem 0 0 0;
}

/* Controls Dropdown & Live Status Bar */
.analytics-controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .analytics-controls {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  width: 100%;
  max-width: 380px;
}

.control-label {
  font-size: 0.725rem;
  font-weight: 600;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.station-dropdown-select {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background-color: #fbfaf8;
  border: 1px solid #ded9d2;
  border-radius: 8px;
  font-size: 0.825rem;
  color: #292524;
  outline: none;
  transition: border-color 0.15s ease;
}

.station-dropdown-select:focus {
  border-color: #52796f;
}

/* Real-Time Node Status Pill */
.node-status-panel {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.45rem 0.75rem;
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 8px;
  align-self: flex-start;
}

@media (min-width: 640px) {
  .node-status-panel {
    align-self: flex-end;
  }
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.status-online {
  background-color: #e4ede9;
  color: #385a50;
}

.status-online .status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #52796f;
  animation: pulseDot 1.6s infinite;
}

.status-unavailable {
  background-color: #f9e6e4;
  color: #9e2a2b;
}

.status-unavailable .status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #b9383a;
}

.last-heartbeat-text {
  font-size: 0.75rem;
  color: #78716c;
  font-variant-numeric: tabular-nums;
}

@keyframes pulseDot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

/* Stats Summary Strip */
.stats-summary-strip {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (min-width: 860px) {
  .stats-summary-strip {
    grid-template-columns: repeat(4, 1fr);
  }
}

.stat-box-mini {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 8px;
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-box-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: #8c857b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stat-box-value {
  font-size: 1.35rem;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.02em;
}

.text-amber {
  color: #8c5b24;
}

.text-sage {
  color: #385a50;
}

/* Chart Container */
.chart-card-container {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.chart-title-bar {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid #eeeae4;
}

@media (min-width: 640px) {
  .chart-title-bar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.chart-title-text {
  font-size: 0.88rem;
  font-weight: 600;
  color: #292524;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.chart-tag-text {
  font-size: 0.68rem;
  font-weight: 600;
  color: #8c857b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.chart-canvas-box {
  width: 100%;
  height: 320px;
  position: relative;
}

@media (min-width: 768px) {
  .chart-canvas-box {
    height: 380px;
  }
}

.chart-loading-box,
.chart-empty-box {
  height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: #f7f6f4;
  border-radius: 8px;
  border: 1px dashed #ded9d2;
}

.loading-msg,
.empty-msg {
  font-size: 0.75rem;
  color: #78716c;
  margin: 0;
}

.empty-heading {
  font-size: 0.88rem;
  font-weight: 600;
  color: #44403c;
  margin: 0;
}
</style>