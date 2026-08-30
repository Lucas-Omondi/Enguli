<template>
  <div class="storage-model-page">
    <!-- Header Section -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Sand Dam Volumetric Model</h1>
        <p class="page-subtitle">Hydrogeological storage calculation, saturated thickness, and water reserve projections.</p>
      </div>

      <!-- Station Selector -->
      <div class="station-select-group">
        <label for="stationSelect" class="select-label">Select Station Transect:</label>
        <select
            id="stationSelect"
            v-model="selectedStationId"
            @change="runModelCalculation"
            class="station-select"
            :disabled="isLoadingStations"
        >
          <option v-for="st in stations" :key="st.id" :value="st.id">
            {{ st.station_code }} - {{ st.station_name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Main Grid: Parameters on Left, Hydrological Output on Right -->
    <div class="model-grid">
      <!-- Left Column: Reservoir Geometry & Hydrogeology Inputs -->
      <div class="card parameters-card">
        <div class="card-header">
          <div class="header-icon-badge">
            <i class="pi pi-sliders-h"></i>
          </div>
          <div>
            <h2 class="card-title">Hydraulic & Bed Parameters</h2>
            <span class="card-desc">Adjust sand reservoir dimensions and specific yield</span>
          </div>
        </div>

        <form @submit.prevent="runModelCalculation" class="parameters-form">
          <div class="input-row">
            <div class="form-field">
              <label class="field-label">
                <span>Reservoir Length ($L$)</span>
                <span class="unit-pill">Meters</span>
              </label>
              <input
                  v-model.number="params.length_m"
                  type="number"
                  step="1"
                  min="10"
                  class="num-input"
                  required
              />
              <span class="field-hint">Length along the river transect</span>
            </div>

            <div class="form-field">
              <label class="field-label">
                <span>Average Bed Width ($W$)</span>
                <span class="unit-pill">Meters</span>
              </label>
              <input
                  v-model.number="params.width_m"
                  type="number"
                  step="0.5"
                  min="2"
                  class="num-input"
                  required
              />
              <span class="field-hint">Mean width between river banks</span>
            </div>
          </div>

          <div class="input-row">
            <div class="form-field">
              <label class="field-label">
                <span>Sand Bed Depth ($D_{bed}$)</span>
                <span class="unit-pill">Meters</span>
              </label>
              <input
                  v-model.number="params.bed_depth_m"
                  type="number"
                  step="0.1"
                  min="0.5"
                  class="num-input"
                  required
              />
              <span class="field-hint">Depth to impermeable bedrock</span>
            </div>

            <div class="form-field">
              <label class="field-label">
                <span>Drainable Porosity ($S_y$)</span>
                <span class="unit-pill">Ratio</span>
              </label>
              <input
                  v-model.number="params.specific_yield"
                  type="number"
                  step="0.01"
                  min="0.10"
                  max="0.45"
                  class="num-input"
                  required
              />
              <span class="field-hint">Coarse river sand typically 0.25 – 0.35</span>
            </div>
          </div>

          <div class="form-field">
            <label class="field-label">
              <span>Daily Water Demand ($Q_{demand}$)</span>
              <span class="unit-pill">m³/day</span>
            </label>
            <input
                v-model.number="params.daily_demand_m3"
                type="number"
                step="1"
                min="1"
                class="num-input"
                required
            />
            <span class="field-hint">Combined domestic and smallholder irrigation extraction</span>
          </div>

          <button type="submit" class="submit-calc-btn" :disabled="isCalculating">
            <i v-if="isCalculating" class="pi pi-spin pi-spinner"></i>
            <i v-else class="pi pi-calculator"></i>
            <span>{{ isCalculating ? 'Re-evaluating Hydrology...' : 'Update Storage Projections' }}</span>
          </button>
        </form>
      </div>

      <!-- Right Column: Volumetric Results & Storage Tank Gauge -->
      <div class="results-column">
        <!-- Capacity Gauge Card -->
        <div class="card gauge-card">
          <div class="card-header">
            <div class="header-icon-badge water-badge">
              <i class="pi pi-database"></i>
            </div>
            <div>
              <h2 class="card-title">Live Storage Capacity</h2>
              <span class="card-desc">Current extractable water in the sand matrix</span>
            </div>
          </div>

          <div v-if="results" class="gauge-content">
            <!-- Percentage Storage Bar -->
            <div class="storage-bar-wrapper">
              <div class="storage-bar-labels">
                <span class="storage-percent-num">{{ results.percentage_full }}%</span>
                <span class="storage-status-text">
                  {{ results.percentage_full > 50 ? 'Optimal Water Storage' : results.percentage_full > 25 ? 'Moderate Depletion' : 'Critical Water Deficit' }}
                </span>
              </div>
              <div class="storage-progress-track">
                <div
                    class="storage-progress-fill"
                    :style="{ width: `${Math.min(100, Math.max(0, results.percentage_full))}%` }"
                    :class="{
                    'fill-high': results.percentage_full >= 50,
                    'fill-medium': results.percentage_full >= 25 && results.percentage_full < 50,
                    'fill-low': results.percentage_full < 25
                  }"
                ></div>
              </div>
            </div>

            <!-- Key Metric Metrics Cards -->
            <div class="metrics-summary-grid">
              <div class="metric-pill-box">
                <span class="metric-lbl">Extractable Volume</span>
                <span class="metric-val">{{ results.current_extractable_volume_m3.toLocaleString() }} <small>m³</small></span>
                <span class="metric-sub">Max: {{ results.max_storage_capacity_m3.toLocaleString() }} m³</span>
              </div>

              <div class="metric-pill-box">
                <span class="metric-lbl">Water Security Horizon</span>
                <span class="metric-val accent-val">{{ results.estimated_days_remaining }} <small>Days</small></span>
                <span class="metric-sub">At {{ params.daily_demand_m3 }} m³/day extraction</span>
              </div>

              <div class="metric-pill-box">
                <span class="metric-lbl">Water Table Depth</span>
                <span class="metric-val">{{ results.water_table_depth_m }} <small>m</small></span>
                <span class="metric-sub">From ground surface</span>
              </div>

              <div class="metric-pill-box">
                <span class="metric-lbl">Saturated Sand Column</span>
                <span class="metric-val">{{ results.saturated_thickness_m }} <small>m</small></span>
                <span class="metric-sub">Active wet thickness</span>
              </div>
            </div>

            <!-- Civil Engineering Hydro Formula Box -->
            <div class="formula-box">
              <span class="formula-title">Governing Saturated Volumetric Relationship</span>
              <code>V_extractable = L × W × (D_bed - d_water) × S_y</code>
              <span class="formula-meta">
                Total Sand Matrix Volume: <strong>{{ results.total_sand_volume_m3.toLocaleString() }} m³</strong>
              </span>
            </div>
          </div>

          <div v-else class="empty-state">
            <i class="pi pi-spin pi-spinner text-2xl text-stone-400"></i>
            <span>Loading telemetry transect data...</span>
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
const selectedStationId = ref(null);
const isLoadingStations = ref(true);
const isCalculating = ref(false);

const params = reactive({
  length_m: 250,
  width_m: 20,
  bed_depth_m: 4.5,
  specific_yield: 0.28,
  daily_demand_m3: 50
});

const results = ref(null);

const fetchStations = async () => {
  isLoadingStations.value = true;
  try {
    const response = await api.getStations();
    stations.value = response.data.results || response.data || [];
    if (stations.value.length > 0) {
      selectedStationId.value = stations.value[0].id;
      await runModelCalculation();
    }
  } catch (error) {
    console.error('Failed to load stations for storage model:', error);
  } finally {
    isLoadingStations.value = false;
  }
};

const runModelCalculation = async () => {
  if (!selectedStationId.value) return;
  isCalculating.value = true;
  try {
    const response = await api.calculateStorageModel({
      station_id: selectedStationId.value,
      ...params
    });
    results.value = response.data.hydrology_metrics;
  } catch (error) {
    console.error('Storage model calculation failed:', error);
  } finally {
    isCalculating.value = false;
  }
};

onMounted(() => {
  fetchStations();
});
</script>

<style scoped>
.storage-model-page {
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

.station-select-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.select-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #57534e;
}

.station-select {
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  border: 1px solid #ded9d2;
  background-color: #fcfbf9;
  font-size: 0.82rem;
  font-weight: 600;
  color: #292524;
  cursor: pointer;
  outline: none;
}

.model-grid {
  display: grid;
  grid-template-columns: 1fr 1.25fr;
  gap: 1.25rem;
}

@media (max-width: 1024px) {
  .model-grid {
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

.water-badge {
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

.parameters-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.field-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.76rem;
  font-weight: 600;
  color: #44403c;
}

.unit-pill {
  font-size: 0.65rem;
  font-weight: 600;
  background-color: #eeeae4;
  color: #78716c;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.num-input {
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  border: 1px solid #ded9d2;
  background-color: #ffffff;
  font-size: 0.85rem;
  font-weight: 600;
  color: #292524;
  outline: none;
}

.num-input:focus {
  border-color: #52796f;
}

.field-hint {
  font-size: 0.66rem;
  color: #a8a29e;
}

.submit-calc-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem;
  background-color: #52796f;
  color: #fdfdfc;
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease;
  margin-top: 0.5rem;
}

.submit-calc-btn:hover {
  background-color: #436b5f;
}

.submit-calc-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Right Column Results */
.gauge-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.storage-bar-wrapper {
  background-color: #f5f3ef;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.storage-bar-labels {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.storage-percent-num {
  font-size: 1.85rem;
  font-weight: 800;
  color: #292524;
  line-height: 1;
}

.storage-status-text {
  font-size: 0.78rem;
  font-weight: 600;
  color: #52796f;
}

.storage-progress-track {
  width: 100%;
  height: 12px;
  background-color: #ded9d2;
  border-radius: 9999px;
  overflow: hidden;
}

.storage-progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}

.fill-high {
  background-color: #52796f;
}

.fill-medium {
  background-color: #d97706;
}

.fill-low {
  background-color: #dc2626;
}

.metrics-summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.metric-pill-box {
  background-color: #fcfbf9;
  border: 1px solid #e7e3dc;
  border-radius: 8px;
  padding: 0.75rem 0.85rem;
  display: flex;
  flex-direction: column;
}

.metric-lbl {
  font-size: 0.68rem;
  font-weight: 600;
  color: #8c857b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-val {
  font-size: 1.25rem;
  font-weight: 700;
  color: #292524;
  margin: 0.15rem 0;
}

.metric-val small {
  font-size: 0.72rem;
  font-weight: 500;
  color: #78716c;
}

.accent-val {
  color: #385a50;
}

.metric-sub {
  font-size: 0.66rem;
  color: #a8a29e;
}

.formula-box {
  background-color: #eeeae4;
  border-radius: 8px;
  padding: 0.75rem 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.formula-title {
  font-size: 0.68rem;
  font-weight: 700;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.formula-box code {
  font-family: monospace;
  font-size: 0.78rem;
  font-weight: 600;
  color: #383533;
}

.formula-meta {
  font-size: 0.72rem;
  color: #57534e;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  gap: 0.5rem;
  color: #8c857b;
}
</style>