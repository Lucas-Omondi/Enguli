<template>
  <div class="tables-view-wrapper">

    <div class="tables-header-container">
      <div>
        <h1 class="tables-main-title">System Logs Audit</h1>
        <p class="tables-subtitle-text">Historical database telemetry readings streamed from the Enguli basin network.</p>
      </div>
    </div>

    <div class="table-summary-grid">
      <div class="summary-widget-card">
        <div class="widget-text-left">
          <span class="widget-label-title">Total Database Rows</span>
          <span class="widget-numeric-value">{{ telemetryLogs.length }}</span>
        </div>
        <div class="widget-icon-frame text-emerald-600 bg-emerald-50/30">
          <i class="pi pi-database"></i>
        </div>
      </div>

      <div class="summary-widget-card">
        <div class="widget-text-left">
          <span class="widget-label-title">Active Outages / Anomalies</span>
          <span class="widget-numeric-value text-amber-600">{{ activeAlertCount }}</span>
        </div>
        <div class="widget-icon-frame text-amber-600 bg-amber-50/30">
          <i class="pi pi-exclamation-circle animate-pulse"></i>
        </div>
      </div>

      <div class="summary-widget-card">
        <div class="widget-text-left">
          <span class="widget-label-title">Basin Network Health</span>
          <span class="widget-numeric-value text-slate-800">98.2%</span>
        </div>
        <div class="widget-icon-frame text-blue-600 bg-blue-50/30">
          <i class="pi pi-wifi"></i>
        </div>
      </div>
    </div>

    <div class="data-table-card">
      <div class="overflow-x-auto" v-if="telemetryLogs.length > 0">
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
            <td class="table-data-cell font-medium text-slate-500 text-xs">
              {{ formatFullDate(log.timestamp) }}
            </td>

            <td class="table-data-cell text-slate-900 font-bold">
              {{ log.station_code }}
            </td>

            <td class="table-data-cell font-bold text-slate-800">
              {{ log.water_level.toFixed(2) }}m
            </td>

            <td class="table-data-cell">
              <div class="flex items-center space-x-2">
                <div class="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden hidden sm:block">
                  <div
                      class="h-full rounded-full transition-all duration-300"
                      :class="log.battery_level < 20 ? 'bg-rose-500' : 'bg-emerald-500'"
                      :style="{ width: log.battery_level + '%' }"
                  ></div>
                </div>
                <span class="text-xs font-semibold text-slate-600">{{ log.battery_level }}%</span>
              </div>
            </td>

            <td class="table-data-cell font-mono text-xs text-slate-500">
                <span class="flex items-center gap-1">
                  <i class="pi pi-signal text-slate-400"></i>
                  {{ log.signal_strength ? log.signal_strength + ' dBm' : '---' }}
                </span>
            </td>

            <td class="table-data-cell">
                <span :class="log.water_level <= 0.5 ? 'table-badge-critical' : 'table-badge-optimal'">
                  <span class="h-1 w-1 rounded-full bg-current"></span>
                  {{ log.water_level <= 0.5 ? 'Low Supply' : 'Optimal' }}
                </span>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <div class="p-12 text-center" v-else>
        <div class="h-12 w-12 rounded-2xl bg-slate-50 border border-slate-100 text-slate-400 flex items-center justify-center mx-auto shadow-inner mb-3">
          <i class="pi pi-folder-open text-lg"></i>
        </div>
        <h3 class="text-sm font-bold text-slate-700">No Historical Records Found</h3>
        <p class="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
          The database currently contains no telemetry history entries. Deploy sensor hardware inputs to stream rows.
        </p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

// Separate Style Component Sheet Pipeline Integration
import '../assets/styles/tables.css';

const telemetryLogs = ref([]);
const activeAlertCount = ref(0);

const loadHistoricalLogsTable = async () => {
  try {
    // 1. Fetch live unresolved counts from your alert service
    const alertsResponse = await api.getActiveAlerts();
    activeAlertCount.value = alertsResponse.data?.length || 0;

    // 2. Query your actual live telemetry readings from your new backend viewset
    const response = await api.getTelemetryLogs();
    const realLogs = response.data; // Array of real database objects

    // 3. Map your Django database keys directly into your table template variables
    telemetryLogs.value = realLogs.map(log => ({
      id: log.id,
      timestamp: log.timestamp,
      station_code: log.station_code, // Uses the direct string returned by our serializer
      water_level: log.water_level,
      battery_level: log.battery_level_snapshot || 0,
      signal_strength: log.signal_strength
    }));

  } catch (error) {
    console.error("Error reading database log history tables:", error);
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