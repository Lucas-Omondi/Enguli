<template>
  <div class="reports-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Hydrological Reports & Data Dossiers</h1>
        <p class="page-subtitle">Generate regulatory filings, seasonal time-series extracts, and CSV datasets for research.</p>
      </div>
    </div>

    <!-- Export Configurations Grid -->
    <div class="reports-grid">
      <!-- Left: Export Builder Card -->
      <div class="card config-card">
        <div class="card-header">
          <div class="header-icon-badge">
            <i class="pi pi-download"></i>
          </div>
          <div>
            <h2 class="card-title">Telemetry Export Builder</h2>
            <span class="card-desc">Configure date parameters and target transects</span>
          </div>
        </div>

        <form @submit.prevent="handleDownloadCSV" class="export-form">
          <!-- Station Selection -->
          <div class="form-field">
            <label class="field-label">Target Station Transect</label>
            <select v-model="filters.station_id" class="custom-select">
              <option value="">All Stations (Complete River Basin)</option>
              <option v-for="st in stations" :key="st.id" :value="st.id">
                {{ st.station_code }} - {{ st.station_name }}
              </option>
            </select>
          </div>

          <!-- Date Range Inputs -->
          <div class="input-row">
            <div class="form-field">
              <label class="field-label">Start Date</label>
              <input
                  v-model="filters.start_date"
                  type="date"
                  class="date-input"
              />
            </div>
            <div class="form-field">
              <label class="field-label">End Date</label>
              <input
                  v-model="filters.end_date"
                  type="date"
                  class="date-input"
              />
            </div>
          </div>

          <!-- Quick Range Presets -->
          <div class="presets-row">
            <span class="preset-label">Quick Presets:</span>
            <button type="button" class="preset-btn" @click="setPresetDays(7)">Last 7 Days</button>
            <button type="button" class="preset-btn" @click="setPresetDays(30)">Last 30 Days</button>
            <button type="button" class="preset-btn" @click="setPresetDays(90)">Full Quarter</button>
            <button type="button" class="preset-btn" @click="clearDates">All Time</button>
          </div>

          <!-- Export Action Button -->
          <button type="submit" class="download-submit-btn" :disabled="isDownloading">
            <i v-if="isDownloading" class="pi pi-spin pi-spinner"></i>
            <i v-else class="pi pi-file-excel"></i>
            <span>{{ isDownloading ? 'Generating CSV File...' : 'Download Telemetry Dataset (CSV)' }}</span>
          </button>
        </form>
      </div>

      <!-- Right: Regulatory & Audit Dossier Guide -->
      <div class="card info-card">
        <div class="card-header">
          <div class="header-icon-badge info-badge">
            <i class="pi pi-book"></i>
          </div>
          <div>
            <h2 class="card-title">Compliance & Formats</h2>
            <span class="card-desc">Water Resource Authority (WRA) data schema</span>
          </div>
        </div>

        <div class="dossier-details">
          <div class="standard-spec-box">
            <span class="spec-title">Standard Telemetry Schema</span>
            <ul class="spec-list">
              <li><strong>Record Timestamp:</strong> Normalized UTC ISO-8601</li>
              <li><strong>Calibrated Water Depth:</strong> Inverted transducer offset ($m$)</li>
              <li><strong>Hardware Diagnostics:</strong> Battery charge ($V/\%$) and RSSI signal</li>
              <li><strong>Spatial Identifiers:</strong> Station code, transect name, and sensor serial</li>
            </ul>
          </div>

          <div class="compliance-note">
            <i class="pi pi-info-circle"></i>
            <p>
              Data files downloaded from this portal comply with hydrological time-series standards for seasonal aquifer recharge audits.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import api from '../api';

const stations = ref([]);
const isDownloading = ref(false);

const filters = reactive({
  station_id: '',
  start_date: '',
  end_date: ''
});

const fetchStations = async () => {
  try {
    const response = await api.getStations();
    stations.value = response.data.results || response.data || [];
  } catch (error) {
    console.error('Failed to load stations for export options:', error);
  }
};

const setPresetDays = (days) => {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - days);

  filters.end_date = end.toISOString().split('T')[0];
  filters.start_date = start.toISOString().split('T')[0];
};

const clearDates = () => {
  filters.start_date = '';
  filters.end_date = '';
};

const handleDownloadCSV = async () => {
  isDownloading.value = true;
  try {
    const params = {};
    if (filters.station_id) params.station_id = filters.station_id;
    if (filters.start_date) params.start_date = filters.start_date;
    if (filters.end_date) params.end_date = filters.end_date;

    const response = await api.exportTelemetryCSV(params);

    // Create a virtual download link from the blob
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');

    const timestamp = new Date().toISOString().split('T')[0];
    link.href = url;
    link.setAttribute('download', `enguli_telemetry_export_${timestamp}.csv`);
    document.body.appendChild(link);
    link.click();

    // Clean up DOM object
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('CSV download failed:', error);
  } finally {
    isDownloading.value = false;
  }
};

onMounted(() => {
  fetchStations();
});
</script>

<style scoped>
.reports-page {
  padding: 1.5rem;
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
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

.reports-grid {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .reports-grid {
    grid-template-columns: 1fr;
  }
}

.card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid #eeeae4;
  padding-bottom: 0.85rem;
}

.header-icon-badge {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background-color: #eeeae4;
  color: #57534e;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
}

.info-badge {
  background-color: #e5ede8;
  color: #385a50;
}

.card-title {
  font-size: 0.96rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
}

.card-desc {
  font-size: 0.72rem;
  color: #8c857b;
}

.export-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  font-size: 0.76rem;
  font-weight: 600;
  color: #44403c;
}

.custom-select, .date-input {
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #ded9d2;
  background-color: #ffffff;
  font-size: 0.82rem;
  font-weight: 500;
  color: #292524;
  outline: none;
}

.custom-select:focus, .date-input:focus {
  border-color: #52796f;
}

.input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.presets-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding: 0.5rem 0;
}

.preset-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #8c857b;
  margin-right: 0.2rem;
}

.preset-btn {
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  border: 1px solid #ded9d2;
  background-color: #f0ece6;
  font-size: 0.7rem;
  font-weight: 600;
  color: #57534e;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-btn:hover {
  background-color: #e5dfd7;
  color: #292524;
}

.download-submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #52796f;
  color: #fdfdfc;
  border: none;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease;
  margin-top: 0.5rem;
}

.download-submit-btn:hover {
  background-color: #436b5f;
}

.download-submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Compliance Column */
.dossier-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.standard-spec-box {
  background-color: #f5f3ef;
  border-radius: 8px;
  padding: 0.9rem;
  border: 1px solid #e7e3dc;
}

.spec-title {
  font-size: 0.76rem;
  font-weight: 700;
  color: #383533;
  margin-bottom: 0.5rem;
  display: block;
}

.spec-list {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.74rem;
  color: #57534e;
  line-height: 1.6;
}

.compliance-note {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  background-color: #e5ede8;
  border: 1px solid #c9ded3;
  border-radius: 8px;
  padding: 0.75rem 0.9rem;
  color: #385a50;
  font-size: 0.73rem;
  line-height: 1.4;
}

.compliance-note i {
  font-size: 0.95rem;
  margin-top: 0.1rem;
}
</style>