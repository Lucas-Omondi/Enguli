<template>
  <div class="analytics-wrapper">

    <div class="analytics-header">
      <div>
        <h1 class="analytics-title">Hydrological Analytics</h1>
        <p class="analytics-subtitle">Time-series aquifer dynamics and abstraction tracking parameters.</p>
      </div>
    </div>

    <div class="analytics-controls">
      <div>
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

    <div class="stats-summary-strip">
      <div class="stat-box-mini">
        <span class="stat-box-label">Station ID Code</span>
        <span class="stat-box-value text-slate-700">{{ activeStationDetails.code }}</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Average Water Table</span>
        <span class="stat-box-value text-slate-900">{{ metrics.avg }}m</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Historical Min (Drawdown)</span>
        <span class="stat-box-value text-amber-600">{{ metrics.min }}m</span>
      </div>
      <div class="stat-box-mini">
        <span class="stat-box-label">Historical Max (Recharge)</span>
        <span class="stat-box-value text-emerald-600">{{ metrics.max }}m</span>
      </div>
    </div>

    <div class="chart-card-container">
      <div class="chart-title-bar">
        <h3 class="chart-title-text">
          <i class="pi pi-chart-line text-emerald-600"></i>
          Groundwater Level Fluctuations & Safety Limits
        </h3>
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Calibrated Values (H - D)</span>
      </div>

      <div class="chart-canvas-box" v-if="loaded">
        <Line :data="chartData" :options="chartOptions" />
      </div>

      <div class="h-[380px] flex items-center justify-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200" v-else>
        <div class="text-center space-y-2">
          <i class="pi pi-spin pi-spinner text-emerald-600 text-2xl"></i>
          <p class="text-xs font-medium text-slate-500">Querying aquifer histories...</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

// Separate Stylesheet Import
import '../assets/styles/analytics.css';

// Chart.js Core Registries Requirements
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

// Operational States Tracking
const loaded = ref(false);
const stations = ref([]);
const selectedStationId = ref(null);
const activeStationDetails = ref({ code: '---' });
const metrics = ref({ avg: '0.00', min: '0.00', max: '0.00' });

// Chart reactive layout nodes datasets
const chartData = ref({ labels: [], datasets: [] });
const chartOptions = ref({});

const initAnalytics = async () => {
  try {
    // 1. Fetch all registered stations from your Django models ViewSet [cite: 2, 28]
    const stationsResponse = await api.getStations();
    stations.value = stationsResponse.data;

    if (stations.value.length > 0) {
      // Pick the first station to populate the premium visual workspace defaults
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
    // Find the station dictionary details to populate label codes
    const matchedStation = stations.value.find(s => s.id === stationId);
    if (matchedStation) {
      activeStationDetails.value = { code: matchedStation.station_code };
    }

    // 2. Load aggregate analysis numbers directly from Django backend [cite: 25]
    const analyticsResponse = await api.getStationAnalytics(stationId);
    const aggs = analyticsResponse.data;

    metrics.value = {
      avg: aggs.average_water_level?.toFixed(2) || '0.00',
      min: aggs.min_water_level?.toFixed(2) || '0.00',
      max: aggs.max_water_level?.toFixed(2) || '0.00'
    };

    // 3. Mock/Populate structural historical time-series curves mapping
    // Note: In your next iteration, we can wire this to a raw historical log dump endpoint!
    const timelineLabels = ['06:00 AM', '09:00 AM', '12:00 PM', '03:00 PM', '06:00 PM', '09:00 PM', '12:00 AM'];
    const historicalReadings = [2.1, 1.8, 1.4, 0.9, 0.45, 1.2, 1.9]; // Sample trend crossing your 0.5m threshold [cite: 17]

    setupChartEngine(timelineLabels, historicalReadings);
    loaded.value = true;
  } catch (error) {
    console.error("Error querying station parameters:", error);
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
        borderColor: '#059669', // Sophisticated Emerald Green matching the brand theme
        borderWidth: 2.5,
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return null;

          // Creates a rich, expensive vertical gradient fill beneath the curve
          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(5, 150, 105, 0.12)');
          gradient.addColorStop(1, 'rgba(5, 150, 105, 0.00)');
          return gradient;
        },
        fill: true,
        tension: 0.35, // Smooth Bezier curves
        pointBackgroundColor: '#059669',
        pointHoverRadius: 6,
        pointRadius: 3
      }
    ]
  };

  chartOptions.value = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }, // Hides bulky legend block for minimalist look
      tooltip: {
        backgroundColor: '#0f172a', // Sleek dark slate tooltip window matching layout sidebar
        titleFont: { size: 11, weight: 'bold' },
        bodyFont: { size: 12 },
        padding: 10,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: (context) => ` Level: ${context.parsed.y} meters`
        }
      }
    },
    scales: {
      x: {
        grid: { display: false }, // Strips away blocky vertical vertical lines
        ticks: { color: '#94a3b8', font: { size: 11 } }
      },
      y: {
        min: 0,
        max: 5, // Maximum aquifer structural constraint reference window
        ticks: {
          color: '#94a3b8',
          font: { size: 11 },
          stepSize: 1,
          callback: (value) => `${value}m`
        },
        grid: { color: '#f1f5f9' } // Crisp thin baseline horizontal separators
      }
    }
  };
};

onMounted(() => {
  initAnalytics();
});
</script>