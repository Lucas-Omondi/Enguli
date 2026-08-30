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
        <span class="metric-value text-amber">{{ metrics.min }}m</span>
      </div>
      <div class="metric-card">
        <span class="metric-label">Maximum Spill Capacity</span>
        <span class="metric-value text-sage">{{ metrics.max }}m</span>
      </div>
    </div>

    <div class="alerts-container">
      <div class="alerts-header">
        <h3 class="alerts-title-text">
          <i class="pi pi-bell text-amber-500 animate-pulse"></i>
          Unresolved System Alerts & Guidance
        </h3>
        <span class="alerts-count-tag">{{ activeAlerts.length }} items pending</span>
      </div>

      <div class="alerts-list" v-if="activeAlerts.length > 0">
        <div v-for="alert in activeAlerts" :key="alert.id" class="alert-row-item">
          <span :class="getBadgeClass(alert.severity)">
            {{ alert.severity.toUpperCase() }}
          </span>
          <div class="alert-info-content">
            <div class="alert-title-bar">
              <h4 class="alert-type-heading">{{ alert.alert_type }}</h4>
              <span class="alert-timestamp">{{ formatTime(alert.created_at) }}</span>
            </div>
            <p class="alert-msg-text">{{ alert.message }}</p>
            <p class="alert-station-ref">Station Ref: {{ alert.station_code }}</p>
          </div>
        </div>
      </div>

      <div class="alerts-empty-box" v-else>
        <i class="pi pi-check-circle text-sage-500 text-3xl"></i>
        <p class="empty-msg">All aquifer parameters optimal. Safe to irrigate.</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const activeAlerts = ref([]);
const metrics = ref({ avg: '0.0', min: '0.0', max: '0.0' });

const loadDashboardData = async () => {
  try {
    const alertsResponse = await api.getActiveAlerts();
    activeAlerts.value = alertsResponse.data || [];

    try {
      const analyticsResponse = await api.getStationAnalytics(1);
      // process analyticsResponse.data ...
    } catch (error) {
      console.warn("Analytics telemetry not yet populated for Station 1:", error);
    }
    const data = analyticsResponse.data;

    metrics.value = {
      avg: typeof data.average_water_level === 'number' ? data.average_water_level.toFixed(2) : '0.00',
      min: typeof data.min_water_level === 'number' ? data.min_water_level.toFixed(2) : '0.00',
      max: typeof data.max_water_level === 'number' ? data.max_water_level.toFixed(2) : '0.00'
    };
  } catch (error) {
    console.error("Dashboard ingestion error:", error);
  }
};

const getBadgeClass = (severity) => {
  const sev = (severity || '').toLowerCase();
  if (sev === 'critical') return 'badge-pill badge-critical';
  if (sev === 'high') return 'badge-pill badge-high';
  return 'badge-pill badge-medium';
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

<style scoped>
/* Page Layout */
.dashboard-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
}

.page-header {
  margin-bottom: 0.25rem;
}

.header-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.02em;
  margin: 0;
}

.header-subtitle {
  font-size: 0.825rem;
  color: #78716c;
  margin: 0.25rem 0 0 0;
}

/* Fluid Responsive Grid: 1 col on mobile, 2 col on tablet, 3 col on desktop */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.85rem;
}

@media (min-width: 640px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Metric Cards: Muted Neutral Stone */
.metric-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.metric-value {
  font-size: 1.75rem;
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

/* Alerts Container */
.alerts-container {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.alerts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid #eeeae4;
}

.alerts-title-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: #292524;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.alerts-count-tag {
  font-size: 0.725rem;
  font-weight: 500;
  color: #8c857b;
}

/* Alerts List */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.alert-row-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.85rem;
  background-color: #f7f6f4;
  border: 1px solid #e7e4df;
  border-radius: 8px;
}

@media (min-width: 640px) {
  .alert-row-item {
    flex-direction: row;
    align-items: flex-start;
    gap: 0.85rem;
  }
}

.alert-info-content {
  flex: 1;
}

.alert-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.alert-type-heading {
  font-size: 0.84rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
}

.alert-timestamp {
  font-size: 0.68rem;
  color: #8c857b;
}

.alert-msg-text {
  font-size: 0.75rem;
  color: #57534e;
  font-weight: 500;
  margin: 0.25rem 0 0 0;
  line-height: 1.35;
}

.alert-station-ref {
  font-size: 0.68rem;
  color: #8c857b;
  font-style: italic;
  margin: 0.25rem 0 0 0;
}

/* Badge System */
.badge-pill {
  display: inline-block;
  align-self: flex-start;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.badge-critical {
  background-color: #faebeb;
  color: #993838;
  border: 1px solid #f3d1d1;
}

.badge-high {
  background-color: #fdf3e7;
  color: #96612b;
  border: 1px solid #fae6cb;
}

.badge-medium {
  background-color: #f0f4f2;
  color: #436b5f;
  border: 1px solid #dae5e0;
}

/* Empty State */
.alerts-empty-box {
  padding: 2rem 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.text-sage-500 {
  color: #52796f;
}

.empty-msg {
  font-size: 0.8rem;
  color: #78716c;
  font-weight: 500;
  margin: 0.5rem 0 0 0;
}
</style>