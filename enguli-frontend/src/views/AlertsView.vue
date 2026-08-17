<template>
  <div class="alerts-page">
    <!-- Header Section -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Alerts & System Health</h1>
        <p class="page-subtitle">Real-time threshold triggers, hardware faults, and hydrological anomaly logs.</p>
      </div>

      <!-- Filter Controls -->
      <div class="filter-group">
        <button
            class="filter-pill"
            :class="{ active: currentFilter === 'all' }"
            @click="setFilter('all')"
        >
          All ({{ totalCount }})
        </button>
        <button
            class="filter-pill"
            :class="{ active: currentFilter === 'active' }"
            @click="setFilter('active')"
        >
          <span class="indicator-dot active-dot"></span>
          Active ({{ activeCount }})
        </button>
        <button
            class="filter-pill"
            :class="{ active: currentFilter === 'resolved' }"
            @click="setFilter('resolved')"
        >
          Resolved ({{ resolvedCount }})
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <i class="pi pi-spin pi-spinner text-2xl text-stone-500"></i>
      <span>Loading system health alerts...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredAlerts.length === 0" class="empty-state">
      <i class="pi pi-check-circle empty-icon"></i>
      <h3 class="empty-title">All Systems Nominal</h3>
      <p class="empty-desc">No {{ currentFilter !== 'all' ? currentFilter : '' }} alerts logged across Enguli telemetry transects.</p>
    </div>

    <!-- Alerts Feed Grid -->
    <div v-else class="alerts-grid">
      <div
          v-for="alert in filteredAlerts"
          :key="alert.id"
          class="alert-card"
          :class="[
          `severity-${alert.severity.toLowerCase()}`,
          { 'is-resolved': alert.is_resolved }
        ]"
      >
        <div class="alert-card-header">
          <div class="severity-badge" :class="alert.severity.toLowerCase()">
            <i :class="getSeverityIcon(alert.severity)"></i>
            <span>{{ alert.severity.toUpperCase() }}</span>
          </div>
          <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
        </div>

        <div class="alert-body">
          <div class="alert-meta">
            <span class="station-tag">
              <i class="pi pi-map-marker"></i>
              {{ alert.station_code }} - {{ alert.station_name }}
            </span>
            <span v-if="alert.sensor_serial" class="sensor-tag">
              <i class="pi pi-microchip"></i>
              {{ alert.sensor_serial }}
            </span>
          </div>

          <h3 class="alert-type-title">{{ formatAlertType(alert.alert_type) }}</h3>
          <p class="alert-message">{{ alert.message }}</p>
        </div>

        <div class="alert-card-footer">
          <div v-if="alert.is_resolved" class="resolved-stamp">
            <i class="pi pi-check"></i>
            <span>Resolved {{ formatTime(alert.resolved_at) }}</span>
          </div>
          <button
              v-else-if="authStore.canManageHardware"
              @click="handleResolveAlert(alert.id)"
              class="resolve-btn"
              :disabled="resolvingId === alert.id"
          >
            <i v-if="resolvingId === alert.id" class="pi pi-spin pi-spinner"></i>
            <i v-else class="pi pi-check"></i>
            <span>Mark Resolved</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const alerts = ref([]);
const isLoading = ref(true);
const resolvingId = ref(null);
const currentFilter = ref('active');

const fetchAlerts = async () => {
  isLoading.value = true;
  try {
    const response = await api.getAlerts();
    alerts.value = response.data.results || response.data || [];
  } catch (error) {
    console.error('Failed to load alerts:', error);
  } finally {
    isLoading.value = false;
  }
};

const setFilter = (filter) => {
  currentFilter.value = filter;
};

const totalCount = computed(() => alerts.value.length);
const activeCount = computed(() => alerts.value.filter(a => !a.is_resolved).length);
const resolvedCount = computed(() => alerts.value.filter(a => a.is_resolved).length);

const filteredAlerts = computed(() => {
  if (currentFilter.value === 'active') return alerts.value.filter(a => !a.is_resolved);
  if (currentFilter.value === 'resolved') return alerts.value.filter(a => a.is_resolved);
  return alerts.value;
});

const handleResolveAlert = async (id) => {
  resolvingId.value = id;
  try {
    await api.resolveAlert(id);
    const target = alerts.value.find(a => a.id === id);
    if (target) {
      target.is_resolved = true;
      target.resolved_at = new Date().toISOString();
    }
  } catch (error) {
    console.error('Failed to resolve alert:', error);
  } finally {
    resolvingId.value = null;
  }
};

const formatTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const formatAlertType = (type) => {
  if (!type) return 'System Notice';
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const getSeverityIcon = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'critical':
    case 'high':
      return 'pi pi-exclamation-triangle';
    case 'medium':
      return 'pi pi-exclamation-circle';
    default:
      return 'pi pi-info-circle';
  }
};

onMounted(() => {
  fetchAlerts();
});
</script>

<style scoped>
.alerts-page {
  padding: 1.5rem;
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
}

.page-subtitle {
  font-size: 0.82rem;
  color: #78716c;
  margin-top: 0.25rem;
}

.filter-group {
  display: flex;
  gap: 0.4rem;
  background-color: #ede8e1;
  padding: 0.25rem;
  border-radius: 9999px;
  border: 1px solid #ded9d2;
}

.filter-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  border-radius: 9999px;
  border: none;
  background: transparent;
  font-size: 0.76rem;
  font-weight: 600;
  color: #57534e;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-pill.active {
  background-color: #fcfbf9;
  color: #292524;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
}

.active-dot {
  background-color: #dc2626;
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1rem;
}

.alert-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.alert-card:hover {
  box-shadow: 0 4px 12px rgba(41, 37, 36, 0.05);
}

.alert-card.is-resolved {
  opacity: 0.75;
  background-color: #f5f3ef;
}

.alert-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.severity-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.severity-badge.critical,
.severity-badge.high {
  background-color: #fee2e2;
  color: #991b1b;
}

.severity-badge.medium {
  background-color: #fef3c7;
  color: #92400e;
}

.severity-badge.low {
  background-color: #e0f2fe;
  color: #075985;
}

.alert-time {
  font-size: 0.7rem;
  color: #a8a29e;
}

.alert-meta {
  display: flex;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
  font-size: 0.72rem;
}

.station-tag, .sensor-tag {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: #57534e;
  font-weight: 600;
  background-color: #eeeae4;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.alert-type-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #292524;
  margin: 0 0 0.35rem 0;
}

.alert-message {
  font-size: 0.8rem;
  color: #57534e;
  line-height: 1.4;
  margin: 0;
}

.alert-card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border-top: 1px solid #eeeae4;
  padding-top: 0.75rem;
}

.resolved-stamp {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #52796f;
}

.resolve-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  background-color: #52796f;
  color: #fdfdfc;
  border: none;
  border-radius: 6px;
  font-size: 0.74rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.resolve-btn:hover {
  background-color: #436b5f;
}

.resolve-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 12px;
  gap: 0.75rem;
  color: #78716c;
}

.empty-icon {
  font-size: 2.25rem;
  color: #52796f;
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
}

.empty-desc {
  font-size: 0.8rem;
  margin: 0;
}
</style>