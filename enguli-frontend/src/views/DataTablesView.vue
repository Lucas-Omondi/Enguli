<template>
  <div class="tables-view-wrapper">

    <!-- Header Section -->
    <div class="tables-header-container">
      <div>
        <h1 class="tables-main-title">System Logs Audit</h1>
        <p class="tables-subtitle-text">Historical database telemetry readings streamed from the Enguli basin network.</p>
      </div>
    </div>

    <!-- Summary Widgets Strip (1 col mobile, 3 col tablet/desktop) -->
    <div class="table-summary-grid">
      <div class="summary-widget-card">
        <div class="widget-text-left">
          <span class="widget-label-title">Total Database Rows</span>
          <span class="widget-numeric-value">{{ telemetryLogs.length }}</span>
        </div>
        <div class="widget-icon-frame icon-sage">
          <i class="pi pi-database"></i>
        </div>
      </div>

      <div class="summary-widget-card">
        <div class="widget-text-left">
          <span class="widget-label-title">Active Outages / Warnings</span>
          <span class="widget-numeric-value text-amber">{{ activeAlertCount }}</span>
        </div>
        <div class="widget-icon-frame icon-amber">
          <i class="pi pi-exclamation-circle"></i>
        </div>
      </div>

      <div class="summary-widget-card">
        <div class="widget-text-left">
          <span class="widget-label-title">Basin Network Health</span>
          <span class="widget-numeric-value text-stone">98.2%</span>
        </div>
        <div class="widget-icon-frame icon-stone">
          <i class="pi pi-wifi"></i>
        </div>
      </div>
    </div>

    <!-- Telemetry Log Container -->
    <div class="data-table-card">
      <div v-if="telemetryLogs.length > 0">

        <!-- Desktop / Tablet Table View -->
        <div class="table-desktop-container">
          <table class="custom-table-element">
            <thead>
            <tr>
              <th class="table-header-cell">Timestamp / Logged</th>
              <th class="table-header-cell">Station Code</th>
              <th class="table-header-cell">Calibrated Level</th>
              <th class="table-header-cell">Node Power</th>
              <th class="table-header-cell">Signal Link</th>
              <th class="table-header-cell">Operational Status</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="log in telemetryLogs" :key="log.id" class="table-row-interactive">
              <td class="table-data-cell text-timestamp">
                {{ formatFullDate(log.timestamp) }}
              </td>

              <td class="table-data-cell text-station">
                {{ log.station_code }}
              </td>

              <td class="table-data-cell text-level">
                {{ typeof log.water_level === 'number' ? log.water_level.toFixed(2) : '0.00' }}m
              </td>

              <td class="table-data-cell">
                <div class="power-meter-wrap">
                  <div class="power-bar-track">
                    <div
                        class="power-bar-fill"
                        :class="log.battery_level < 20 ? 'power-low' : 'power-normal'"
                        :style="{ width: Math.min(log.battery_level, 100) + '%' }"
                    ></div>
                  </div>
                  <span class="power-text">{{ log.battery_level }}%</span>
                </div>
              </td>

              <td class="table-data-cell text-signal">
                  <span class="signal-tag">
                    <i class="pi pi-signal text-[10px]"></i>
                    {{ log.signal_strength ? log.signal_strength + ' dBm' : '---' }}
                  </span>
              </td>

              <td class="table-data-cell">
                  <span :class="log.water_level <= 0.5 ? 'table-badge-critical' : 'table-badge-optimal'">
                    <span class="badge-dot"></span>
                    {{ log.water_level <= 0.5 ? 'Low Supply' : 'Optimal' }}
                  </span>
              </td>
            </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Card Stack View -->
        <div class="mobile-log-stack">
          <div v-for="log in telemetryLogs" :key="'mob-' + log.id" class="mobile-log-card">
            <div class="mobile-card-header">
              <div class="mobile-card-station">
                <span class="station-code-badge">{{ log.station_code }}</span>
                <span class="mobile-timestamp">{{ formatFullDate(log.timestamp) }}</span>
              </div>
              <span :class="log.water_level <= 0.5 ? 'table-badge-critical' : 'table-badge-optimal'">
                <span class="badge-dot"></span>
                {{ log.water_level <= 0.5 ? 'Low Supply' : 'Optimal' }}
              </span>
            </div>

            <div class="mobile-card-grid">
              <div class="mobile-grid-item">
                <span class="grid-label">Water Level</span>
                <span class="grid-value text-level">{{ typeof log.water_level === 'number' ? log.water_level.toFixed(2) : '0.00' }}m</span>
              </div>
              <div class="mobile-grid-item">
                <span class="grid-label">Battery Power</span>
                <span class="grid-value" :class="log.battery_level < 20 ? 'text-low' : 'text-stone'">{{ log.battery_level }}%</span>
              </div>
              <div class="mobile-grid-item">
                <span class="grid-label">Signal Link</span>
                <span class="grid-value text-signal-val">{{ log.signal_strength ? log.signal_strength + ' dBm' : '---' }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Empty State -->
      <div class="empty-table-box" v-else>
        <div class="empty-icon-wrap">
          <i class="pi pi-folder-open text-base"></i>
        </div>
        <h3 class="empty-title">No Historical Records Found</h3>
        <p class="empty-desc">
          The database currently contains no telemetry history entries. Connect sensor hardware inputs to stream rows.
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const telemetryLogs = ref([]);
const activeAlertCount = ref(0);

const loadHistoricalLogsTable = async () => {
  try {
    const alertsResponse = await api.getActiveAlerts();
    activeAlertCount.value = alertsResponse.data?.length || 0;

    const response = await api.getTelemetryLogs();
    const realLogs = response.data || [];

    telemetryLogs.value = realLogs.map(log => ({
      id: log.id,
      timestamp: log.timestamp,
      station_code: log.station_code || 'ENG-01',
      water_level: typeof log.water_level === 'number' ? log.water_level : 0,
      battery_level: log.battery_level_snapshot || 100,
      signal_strength: log.signal_strength
    }));
  } catch (error) {
    console.error("Error reading database log history:", error);
  }
};

const formatFullDate = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

onMounted(() => {
  loadHistoricalLogsTable();
});
</script>

<style scoped>
/* Main View Wrapper */
.tables-view-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
}

.tables-header-container {
  margin-bottom: 0.15rem;
}

.tables-main-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.02em;
  margin: 0;
}

.tables-subtitle-text {
  font-size: 0.825rem;
  color: #78716c;
  margin: 0.25rem 0 0 0;
}

/* Summary Grid: 1 col on mobile, 3 col on tablet/desktop */
.table-summary-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .table-summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.summary-widget-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  padding: 1rem 1.15rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.widget-text-left {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.widget-label-title {
  font-size: 0.68rem;
  font-weight: 600;
  color: #8c857b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.widget-numeric-value {
  font-size: 1.45rem;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.02em;
}

.text-amber {
  color: #8c5b24;
}

.text-stone {
  color: #44403c;
}

.widget-icon-frame {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.icon-sage {
  background-color: #eaf2ed;
  color: #436b5f;
}

.icon-amber {
  background-color: #fcf4e8;
  color: #8c5b24;
}

.icon-stone {
  background-color: #f0ece6;
  color: #6c665e;
}

/* Data Table Card Wrapper */
.data-table-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  overflow: hidden;
}

/* Desktop Table View */
.table-desktop-container {
  display: none;
  width: 100%;
  overflow-x: auto;
}

@media (min-width: 768px) {
  .table-desktop-container {
    display: block;
  }
}

.custom-table-element {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.table-header-cell {
  padding: 0.75rem 1rem;
  font-size: 0.68rem;
  font-weight: 700;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background-color: #f7f6f4;
  border-bottom: 1px solid #eeeae4;
}

.table-row-interactive {
  border-bottom: 1px solid #f2eee8;
  transition: background-color 0.1s ease;
}

.table-row-interactive:hover {
  background-color: #f7f5f0;
}

.table-data-cell {
  padding: 0.8rem 1rem;
  font-size: 0.78rem;
  vertical-align: middle;
}

.text-timestamp {
  color: #78716c;
}

.text-station {
  font-weight: 700;
  color: #292524;
}

.text-level {
  font-weight: 700;
  color: #292524;
}

.text-signal {
  font-family: monospace;
  font-size: 0.72rem;
  color: #78716c;
}

.signal-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

/* Power Meter Bar */
.power-meter-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.power-bar-track {
  width: 50px;
  height: 5px;
  background-color: #eeeae4;
  border-radius: 9999px;
  overflow: hidden;
}

.power-bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.power-normal {
  background-color: #52796f;
}

.power-low {
  background-color: #993838;
}

.power-text {
  font-size: 0.72rem;
  font-weight: 600;
  color: #57534e;
}

/* Status Badges */
.table-badge-optimal,
.table-badge-critical {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.badge-dot {
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background-color: currentColor;
}

.table-badge-optimal {
  background-color: #eaf2ed;
  color: #385a50;
  border: 1px solid #d1e2d7;
}

.table-badge-critical {
  background-color: #faebeb;
  color: #993838;
  border: 1px solid #f3d1d1;
}

/* Mobile Stacked Card View */
.mobile-log-stack {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  gap: 0.65rem;
}

@media (min-width: 768px) {
  .mobile-log-stack {
    display: none;
  }
}

.mobile-log-card {
  background-color: #f7f6f4;
  border: 1px solid #e7e4df;
  border-radius: 8px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.mobile-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mobile-card-station {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.station-code-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: #292524;
}

.mobile-timestamp {
  font-size: 0.68rem;
  color: #8c857b;
}

.mobile-card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #eeeae4;
}

.mobile-grid-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.grid-label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #8c857b;
  text-transform: uppercase;
}

.grid-value {
  font-size: 0.75rem;
  font-weight: 600;
}

.text-low {
  color: #993838;
}

.text-signal-val {
  font-family: monospace;
  color: #78716c;
  font-size: 0.7rem;
}

/* Empty State */
.empty-table-box {
  padding: 2.5rem 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background-color: #f0ece6;
  color: #8c857b;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.6rem;
}

.empty-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
}

.empty-desc {
  font-size: 0.72rem;
  color: #78716c;
  max-width: 280px;
  margin: 0.25rem 0 0 0;
  line-height: 1.4;
}
</style>