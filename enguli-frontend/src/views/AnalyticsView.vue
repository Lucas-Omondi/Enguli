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
    </div>

    <!-- Stats Summary Strip (2-col on mobile, 4-col on desktop) -->
    <div class="stats-summary-strip">
      <div class="stat-box-mini">
        <span class="stat-box-label">Station ID Code</span>
        <span class="stat-box-value">{{ activeStationDetails.code }}</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Average Water Table</span>
        <span class="stat-box-value">{{ metrics.avg }}m</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Historical Min (Drawdown)</span>
        <span class="stat-box-value text-amber">{{ metrics.min }}m</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Historical Max (Recharge)</span>
        <span class="stat-box-value text-sage">{{ metrics.max }}m</span>
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
import { ref, onMounted } from 'vue';
import api from '../api';

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

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, Filler);

const loaded = ref(false);
const stations = ref([]);
const selectedStationId = ref(null);
const activeStationDetails = ref({ code: '---' });
const metrics = ref({ avg: '0.00', min: '0.00', max: '0.00' });

const chartData = ref({ labels: [], datasets: [] });
const chartOptions = ref({});

const initAnalytics = async () => {
  try {
    const stationsResponse = await api.getStations();
    stations.value = stationsResponse.data || [];

    if (stations.value.length > 0) {
      selectedStationId.value = stations.value[0].id;
      await fetchStationData(selectedStationId.value);
    }
  } catch (error) {
    console.error("Hydrological initialization failure:", error);
  }
};

const fetchStationData = async (stationId) => {
  loaded.value = false;
  try {
    const matchedStation = stations.value.find(s => s.id === stationId);
    if (matchedStation) {
      activeStationDetails.value = { code: matchedStation.station_code };
    }

    // 1. Fetch live telemetry logs using the dedicated api helper
    let logs = [];
    if (typeof api.getSensorReadings === 'function') {
      const response = await api.getSensorReadings(stationId);
      logs = response.data?.results || response.data || [];
    } else {
      // Fallback if direct Axios instance is exported
      const response = await api.get(`/api/telemetry/readings/?station_id=${stationId}`);
      logs = response.data?.results || response.data || [];
    }

    if (logs.length > 0) {
      // Reorder from oldest to newest for chronological left-to-right chart plotting
      const chronologicalLogs = [...logs].reverse();

      const timelineLabels = [];
      const waterLevelValues = [];
      let total = 0;
      let minVal = Infinity;
      let maxVal = -Infinity;

      chronologicalLogs.forEach((entry) => {
        if (entry.water_level !== null && entry.water_level !== undefined) {
          const val = Number(entry.water_level);
          waterLevelValues.push(Number(val.toFixed(3)));

          total += val;
          if (val < minVal) minVal = val;
          if (val > maxVal) maxVal = val;

          // Format UTC timestamp to readable local time (e.g., "08:15 PM")
          if (entry.timestamp) {
            const date = new Date(entry.timestamp);
            const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            timelineLabels.push(timeStr);
          } else {
            timelineLabels.push(`Log #${entry.id}`);
          }
        }
      });

      // Calculate real summary statistics from live readings
      const count = waterLevelValues.length;
      if (count > 0) {
        metrics.value = {
          avg: (total / count).toFixed(2),
          min: minVal.toFixed(2),
          max: maxVal.toFixed(2)
        };
      } else {
        metrics.value = { avg: '0.00', min: '0.00', max: '0.00' };
      }

      setupChartEngine(timelineLabels, waterLevelValues);
    } else {
      // No readings recorded yet for this station
      metrics.value = { avg: '0.00', min: '0.00', max: '0.00' };
      setupChartEngine([], []);
    }

    loaded.value = true;
  } catch (error) {
    console.error("Error querying station telemetry parameters:", error);
    metrics.value = { avg: '0.00', min: '0.00', max: '0.00' };
    setupChartEngine([], []);
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
        label: 'Calibrated Water Table Depth (m)',
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
        pointRadius: values.length > 50 ? 0 : 3.5 // Hide individual dots if high density log
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
          label: (context) => ` Water Level: ${context.parsed.y} m`
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
        suggestedMax: 3.5,
        ticks: {
          color: '#8c857b',
          font: { size: 10 },
          callback: (value) => `${value}m`
        },
        grid: { color: '#ece8e1' }
      }
    }
  };
};

onMounted(() => {
  initAnalytics();
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

/* Controls Dropdown */
.analytics-controls {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
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