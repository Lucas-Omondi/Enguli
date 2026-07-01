<template>
  <div class="dashboard-wrapper">

    <div class="page-header">
      <div>
        <h1 class="header-title">Enguli Basin Operations</h1>
        <p class="header-subtitle">Real-time agricultural telemetry and groundwater abstraction monitors.</p>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-card">
        <span class="metric-label">Average Water Level</span>
        <span class="metric-value">{{ metrics.avg }}m</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">Minimum Level (Dry Run)</span>
        <span class="metric-value text-amber-600">{{ metrics.min }}m</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">Maximum Spill Capacity</span>
        <span class="metric-value text-emerald-600">{{ metrics.max }}m</span>
      </div>
    </div>

    <div class="alerts-container">
      <div class="alerts-header">
        <h3 class="alerts-title-text">
          <i class="pi pi-bell text-amber-500 animate-pulse"></i>
          Unresolved System Alerts & Guidance
        </h3>
        <span class="text-xs font-medium text-slate-400">{{ activeAlerts.length }} items pending</span>
      </div>

      <div class="alerts-list" v-if="activeAlerts.length > 0">
        <div v-for="alert in activeAlerts" :key="alert.id" class="alert-row-item">
          <span :class="getBadgeClass(alert.severity)">
            {{ alert.severity.toUpperCase() }}
          </span>
          <div class="flex-1">
            <div class="flex items-center justify-between">
              <h4 class="text-sm font-bold text-slate-800">{{ alert.alert_type }}</h4>
              <span class="text-[11px] text-slate-400">{{ formatTime(alert.created_at) }}</span>
            </div>
            <p class="text-xs text-slate-600 mt-1 font-medium">{{ alert.message }}</p>
            <p class="text-[11px] text-slate-400 mt-1 italic">Station Ref: {{ alert.station_code }}</p>
          </div>
        </div>
      </div>

      <div class="p-8 text-center" v-else>
        <i class="pi pi-check-circle text-emerald-500 text-3xl"></i>
        <p class="text-sm text-slate-500 font-medium mt-2">All aquifer parameters optimal. Safe to irrigate.</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api'; // Your centralized axios connector

// Import separate component style sheets directly into the build workspace
import '../assets/styles/dashboard.css';

const activeAlerts = ref([]);
const metrics = ref({ avg: '0.0', min: '0.0', max: '0.0' });

const loadDashboardData = async () => {
  try {
    // 1. Fetch live un-resolved alerts feed to keep farmers notified
    const alertsResponse = await api.getActiveAlerts();
    activeAlerts.value = alertsResponse.data;

    // 2. Fetch data analytics aggregates for your first station node as an introductory layout standard
    const analyticsResponse = await api.getStationAnalytics(1);
    const data = analyticsResponse.data;

    metrics.value = {
      avg: data.average_water_level?.toFixed(2) || '0.00',
      min: data.min_water_level?.toFixed(2) || '0.00',
      max: data.max_water_level?.toFixed(2) || '0.00'
    };
  } catch (error) {
    console.error("Dashboard ingestion error:", error);
  }
};

const getBadgeClass = (severity) => {
  if (severity === 'critical') return 'badge-critical';
  if (severity === 'high') return 'badge-high';
  return 'badge-medium';
};

const formatTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

onMounted(() => {
  loadDashboardData();
});
</script>