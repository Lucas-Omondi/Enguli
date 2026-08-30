<template>
  <div class="stations-view-split-layout">
    <!-- Map Canvas Panel with Action Overlay -->
    <div class="map-container-wrapper">
      <div ref="mapContainer" class="map-canvas-panel"></div>

      <!-- Management Quick Action Header (Only for Admin / Field Engineer) -->
      <div v-if="authStore.canManageHardware" class="map-actions-overlay">
        <button @click="showAddStationModal = true" class="action-btn primary-action-btn">
          <i class="pi pi-plus text-xs"></i>
          <span>Add Station</span>
        </button>
      </div>
    </div>

    <!-- Station Inspector Panel -->
    <aside class="station-inspector-panel" v-if="activeStation">
      <div class="inspector-header-box">
        <div class="inspector-header-top">
          <span class="inspector-station-code">{{ activeStation.station_code }}</span>
          <span :class="getStatusClass(activeStation.status)">
            {{ activeStation.status }}
          </span>
        </div>
        <h2 class="inspector-station-name">{{ activeStation.station_name }}</h2>
        <p class="inspector-location-desc">
          <strong>Site Notes:</strong> {{ activeStation.location_description || 'No location description logs registered for this observation point.' }}
        </p>
      </div>

      <div class="inspector-body-scroll">
        <!-- Georeferencing Details -->
        <div class="hardware-diagnostics-card">
          <h4 class="diagnostics-card-title">Spatial Georeferencing</h4>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Latitude Coordinate</span>
            <span class="diagnostic-value">{{ activeStation.latitude?.toFixed(6) }}° N</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Longitude Coordinate</span>
            <span class="diagnostic-value">{{ activeStation.longitude?.toFixed(6) }}° E</span>
          </div>
        </div>

        <!-- Telemetry Sensor Asset Details -->
        <div class="hardware-diagnostics-card" v-if="activeSensor">
          <div class="flex items-center justify-between mb-1">
            <h4 class="diagnostics-card-title m-0">Telemetry Sensor Asset</h4>
            <span class="sensor-count-badge">{{ activeStation.sensors?.length || 1 }} Linked</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Sensor Code</span>
            <span class="diagnostic-value">{{ activeSensor.sensor_code || '---' }}</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Sensor Type</span>
            <span class="diagnostic-value capitalize">{{ activeSensor.sensor_type }}</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Hardware Serial</span>
            <span class="diagnostic-value font-mono">{{ activeSensor.serial_number }}</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Offset Height (H)</span>
            <span class="diagnostic-value text-sage">{{ activeSensor.calibration_offset?.toFixed(2) }}m</span>
          </div>
          <div class="diagnostic-data-row border-top-divider">
            <span class="diagnostic-label">Node Battery Charge</span>
            <span class="battery-readout" :class="activeSensor.battery_level < 20 ? 'battery-low' : 'battery-normal'">
              <i class="pi" :class="activeSensor.battery_level < 20 ? 'pi-battery-down' : 'pi-battery-up'"></i>
              {{ activeSensor.battery_level }}%
            </span>
          </div>
        </div>

        <!-- Unlinked Sensor State -->
        <div class="empty-sensor-card" v-else>
          <p class="m-0 mb-2">No hardware sensor profile linked to this station.</p>
          <button
              v-if="authStore.canManageHardware"
              @click="openAddSensorModal"
              class="action-btn secondary-action-btn"
          >
            <i class="pi pi-plus text-xs"></i>
            <span>Register Sensor</span>
          </button>
        </div>

        <!-- Register Sensor Button (if sensor already exists, but user wants to add an extra node) -->
        <button
            v-if="authStore.canManageHardware && activeSensor"
            @click="openAddSensorModal"
            class="add-extra-sensor-btn"
        >
          <i class="pi pi-plus text-xs"></i> Add Another Sensor Node
        </button>
      </div>

      <!-- Action Footer Link -->
      <div class="inspector-action-footer">
        <router-link to="/analytics" class="pivot-analytics-btn">
          <i class="pi pi-chart-bar"></i>
          Inspect Aquifer Analytics Timeline
        </router-link>
      </div>
    </aside>

    <!-- Empty / No Selection State -->
    <aside class="station-inspector-panel inspector-empty-panel" v-else>
      <i class="pi pi-map text-stone-400 text-3xl"></i>
      <h3 class="empty-heading">No Station Highlighted</h3>
      <p class="empty-text">
        Select an observation well pinpoint from the map canvas to inspect hardware diagnostics.
      </p>
    </aside>

    <!-- Modal 1: Add Station -->
    <div v-if="showAddStationModal" class="modal-backdrop" @click.self="showAddStationModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">Register Observation Station</h3>
          <button @click="showAddStationModal = false" class="modal-close-btn">&times;</button>
        </div>

        <form @submit.prevent="submitCreateStation" class="modal-form">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Station Code *</label>
              <input v-model="newStation.station_code" placeholder="e.g. ENG-02" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Status</label>
              <select v-model="newStation.status" class="form-input">
                <option value="active">Active</option>
                <option value="maintenance">Maintenance</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Station Name *</label>
            <input v-model="newStation.station_name" placeholder="e.g. Enguli Lower Basin Well" required class="form-input" />
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Latitude (°N) *</label>
              <input v-model.number="newStation.latitude" type="number" step="any" placeholder="-1.286389" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Longitude (°E) *</label>
              <input v-model.number="newStation.longitude" type="number" step="any" placeholder="36.817223" required class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Site Description Notes</label>
            <textarea v-model="newStation.location_description" rows="3" placeholder="Hydrogeological features, wellhead datum, nearby landmarks..." class="form-input"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showAddStationModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" :disabled="isSubmitting" class="btn-submit">
              <i v-if="isSubmitting" class="pi pi-spin pi-spinner mr-1"></i>
              {{ isSubmitting ? 'Saving...' : 'Create Station' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal 2: Register Sensor -->
    <div v-if="showAddSensorModal" class="modal-backdrop" @click.self="showAddSensorModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <div>
            <h3 class="modal-title">Register Sensor Hardware</h3>
            <span class="modal-subtitle">Station: {{ activeStation?.station_code }} - {{ activeStation?.station_name }}</span>
          </div>
          <button @click="showAddSensorModal = false" class="modal-close-btn">&times;</button>
        </div>

        <form @submit.prevent="submitCreateSensor" class="modal-form">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Sensor Code</label>
              <input v-model="newSensor.sensor_code" placeholder="e.g. SEN-02" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Sensor Type *</label>
              <select v-model="newSensor.sensor_type" required class="form-input">
                <option value="ultrasonic">Ultrasonic</option>
                <option value="pressure">Pressure Transducer</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Serial Number / MAC Identifier *</label>
            <input v-model="newSensor.serial_number" placeholder="e.g. ESP32-94DE69E9BFB4-S2" required class="form-input font-mono" />
          </div>

          <div class="form-group">
            <label class="form-label">Calibration Offset Height (m) *</label>
            <input v-model.number="newSensor.calibration_offset" type="number" step="0.01" placeholder="3.00" required class="form-input" />
            <span class="field-help">Total height $H$ from sensor datum to river sand bed.</span>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showAddSensorModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" :disabled="isSubmitting" class="btn-submit">
              <i v-if="isSubmitting" class="pi pi-spin pi-spinner mr-1"></i>
              {{ isSubmitting ? 'Registering...' : 'Register Sensor' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
const initMapEngine = () => {
  if (!mapContainer.value) return;

  mapInstance = L.map(mapContainer.value, {
    zoomControl: false
  }).setView([-1.286389, 36.817223], 7);

  // CARTO Positron with your API Key
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png?api_key={apiKey}', {
    apiKey: 'cb1_2kum_1_29955f31959fdab35572c322',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(mapInstance);

  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
  markersGroup.addTo(mapInstance);
};

  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
  markersGroup.addTo(mapInstance);
};
const activeSensor = ref(null);

// Modal visibility & form models
const showAddStationModal = ref(false);
const showAddSensorModal = ref(false);
const isSubmitting = ref(false);

const newStation = ref({
  station_code: '',
  station_name: '',
  latitude: null,
  longitude: null,
  location_description: '',
  status: 'active'
});

const newSensor = ref({
  sensor_code: '',
  sensor_type: 'ultrasonic',
  serial_number: '',
  calibration_offset: 3.0
});

const handleResize = () => {
  if (mapInstance) {
    mapInstance.invalidateSize();
  }
};

const initMapEngine = () => {
  if (!mapContainer.value) return;

  mapInstance = L.map(mapContainer.value, {
    zoomControl: false
  }).setView([-1.286389, 36.817223], 7);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mapInstance);

  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
  markersGroup.addTo(mapInstance);
};

const loadStationsFramework = async (targetStationId = null) => {
  try {
    const stationsResponse = await api.getStations();
    stations.value = stationsResponse.data || [];

    markersGroup.clearLayers();

    if (stations.value.length > 0) {
      const boundsArray = [];

      stations.value.forEach((station) => {
        if (station.latitude && station.longitude) {
          const latLng = [station.latitude, station.longitude];
          boundsArray.push(latLng);

          const marker = L.marker(latLng, {
            icon: L.divIcon({
              className: 'custom-map-pin',
              html: `<div class="station-pin"></div>`,
              iconSize: [20, 20],
              iconAnchor: [10, 10]
            })
          });

          marker.on('click', () => {
            inspectStation(station);
            mapInstance.panTo(latLng);
          });

          marker.bindPopup(`<b style="font-weight:600;color:#292524;">${station.station_code}</b><br><span style="font-size:12px;color:#78716c;">${station.station_name}</span>`);
          markersGroup.addLayer(marker);
        }
      });

      if (boundsArray.length > 0 && !targetStationId) {
        mapInstance.fitBounds(boundsArray, { padding: [40, 40] });
      }

      if (targetStationId) {
        const found = stations.value.find(s => s.id === targetStationId);
        if (found) inspectStation(found);
      } else if (!activeStation.value) {
        inspectStation(stations.value[0]);
      }
    }
  } catch (error) {
    console.error("Error pulling coordinate layers:", error);
  }
};

const inspectStation = async (station) => {
  activeStation.value = station;
  activeSensor.value = null;

  try {
    const sensorsResponse = await api.getSensors(station.id);
    if (sensorsResponse.data && sensorsResponse.data.length > 0) {
      activeSensor.value = sensorsResponse.data[0];
    }
  } catch (error) {
    console.error("Error loading node parameters:", error);
  }
};

const openAddSensorModal = () => {
  newSensor.value = {
    sensor_code: '',
    sensor_type: 'ultrasonic',
    serial_number: '',
    calibration_offset: 3.0
  };
  showAddSensorModal.value = true;
};

const submitCreateStation = async () => {
  isSubmitting.value = true;
  try {
    const res = await api.createStation(newStation.value);
    showAddStationModal.value = false;
    newStation.value = {
      station_code: '',
      station_name: '',
      latitude: null,
      longitude: null,
      location_description: '',
      status: 'active'
    };
    await loadStationsFramework(res.data.id);
    if (res.data.latitude && res.data.longitude) {
      mapInstance.setView([res.data.latitude, res.data.longitude], 12);
    }
  } catch (error) {
    console.error("Error creating station:", error);
    alert(error.response?.data?.detail || "Failed to create station. Please verify input parameters.");
  } finally {
    isSubmitting.value = false;
  }
};

const submitCreateSensor = async () => {
  if (!activeStation.value) return;
  isSubmitting.value = true;
  try {
    const payload = {
      ...newSensor.value,
      station: activeStation.value.id
    };
    await api.createSensor(payload);
    showAddSensorModal.value = false;
    await inspectStation(activeStation.value);
  } catch (error) {
    console.error("Error registering sensor:", error);
    alert(error.response?.data?.detail || "Failed to register sensor. Check serial uniqueness.");
  } finally {
    isSubmitting.value = false;
  }
};

const getStatusClass = (status) => {
  const s = (status || '').toLowerCase();
  if (s === 'active') return 'status-pill status-pill-active';
  if (s === 'maintenance') return 'status-pill status-pill-maintenance';
  return 'status-pill status-pill-inactive';
};

onMounted(async () => {
  initMapEngine();
  await nextTick();

  // Force Leaflet to recalculate exact container dimensions
  setTimeout(() => {
    if (mapInstance) {
      mapInstance.invalidateSize();
    }
  }, 200);

  await loadStationsFramework();
  window.addEventListener('resize', handleResize);
});
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (mapInstance) {
    mapInstance.remove();
  }
});
</script>

<style scoped>
/* Split Layout */
.stations-view-split-layout {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  height: calc(100vh - 120px);
  min-height: 550px;
}

@media (min-width: 1024px) {
  .stations-view-split-layout {
    flex-direction: row;
    align-items: stretch;
  }
}

/* Map Canvas Container */
.map-container-wrapper {
  flex: 1;
  min-height: 280px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e7e3dc;
  background-color: #f5f2eb;
  position: relative;
}

@media (min-width: 1024px) {
  .map-container-wrapper {
    flex: 3;
    min-height: 100%;
  }
}

.map-canvas-panel {
  width: 100%;
  height: 100%;
  min-height: 450px;
  z-index: 10;
}

.map-actions-overlay {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 20;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.primary-action-btn {
  background-color: #52796f;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(41, 37, 36, 0.15);
}

.primary-action-btn:hover {
  background-color: #436b5f;
}

.secondary-action-btn {
  background-color: #f0ece6;
  color: #44403c;
  border: 1px solid #ded9d2;
}

.secondary-action-btn:hover {
  background-color: #e5dfd7;
}

/* Inspector Right Panel */
.station-inspector-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 12px;
  overflow: hidden;
}

@media (min-width: 1024px) {
  .station-inspector-panel {
    flex: 2;
    max-width: 440px;
  }
}

.inspector-header-box {
  padding: 1.15rem;
  border-bottom: 1px solid #eeeae4;
  background-color: #f7f6f4;
}

.inspector-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.inspector-station-code {
  font-size: 0.72rem;
  font-weight: 700;
  color: #78716c;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.inspector-station-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
  letter-spacing: -0.01em;
}

.inspector-location-desc {
  font-size: 0.75rem;
  color: #6c665e;
  line-height: 1.4;
  margin: 0.4rem 0 0 0;
}

.inspector-body-scroll {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  overflow-y: auto;
}

.hardware-diagnostics-card {
  background-color: #ffffff;
  border: 1px solid #ece8e1;
  border-radius: 8px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.diagnostics-card-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 0.25rem 0;
}

.sensor-count-badge {
  font-size: 0.65rem;
  font-weight: 600;
  color: #78716c;
  background-color: #f2efe9;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.diagnostic-data-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
}

.diagnostic-label {
  color: #8c857b;
}

.diagnostic-value {
  font-weight: 600;
  color: #292524;
}

.text-sage {
  color: #385a50;
}

.border-top-divider {
  border-top: 1px solid #f2eee8;
  padding-top: 0.4rem;
  margin-top: 0.2rem;
}

.battery-readout {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
  font-size: 0.75rem;
}

.battery-normal {
  color: #385a50;
}

.battery-low {
  color: #993838;
}

.empty-sensor-card {
  padding: 1rem;
  background-color: #fcf8f2;
  border: 1px solid #f2e6d5;
  border-radius: 8px;
  text-align: center;
  font-size: 0.75rem;
  color: #8c5b24;
}

.add-extra-sensor-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.5rem;
  background-color: #f7f6f4;
  border: 1px dashed #ded9d2;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #6c665e;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-extra-sensor-btn:hover {
  background-color: #ede8e1;
  color: #292524;
}

.inspector-action-footer {
  padding: 0.85rem 1rem;
  border-top: 1px solid #eeeae4;
  background-color: #f7f6f4;
}

.pivot-analytics-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  width: 100%;
  padding: 0.55rem 0.85rem;
  background-color: #52796f;
  color: #ffffff;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 0.15s ease;
  box-sizing: border-box;
}

.pivot-analytics-btn:hover {
  background-color: #436b5f;
}

.status-pill {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.status-pill-active {
  background-color: #eaf2ed;
  color: #385a50;
  border: 1px solid #d1e2d7;
}

.status-pill-maintenance {
  background-color: #fcf4e8;
  color: #8c5b24;
  border: 1px solid #fae6cb;
}

.status-pill-inactive {
  background-color: #faebeb;
  color: #993838;
  border: 1px solid #f3d1d1;
}

.inspector-empty-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.empty-heading {
  font-size: 0.85rem;
  font-weight: 600;
  color: #44403c;
  margin: 0.5rem 0 0 0;
}

.empty-text {
  font-size: 0.72rem;
  color: #8c857b;
  max-width: 220px;
  margin: 0.25rem 0 0 0;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eeeae4;
}

.modal-title {
  font-size: 1rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.72rem;
  color: #78716c;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.35rem;
  color: #a8a29e;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-close-btn:hover {
  color: #292524;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.form-input {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background-color: #ffffff;
  border: 1px solid #ded9d2;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #292524;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s ease;
}

.form-input:focus {
  border-color: #52796f;
}

.field-help {
  font-size: 0.65rem;
  color: #8c857b;
  margin-top: 0.15rem;
}

.modal-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eeeae4;
}

.btn-cancel {
  padding: 0.5rem 0.85rem;
  background-color: #f2efe9;
  color: #6c665e;
  border: 1px solid #ded9d2;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #52796f;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background-color: #436b5f;
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>

<style>
.station-pin {
  width: 14px;
  height: 14px;
  background-color: #52796f;
  border: 2px solid #ffffff;
  border-radius: 9999px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.station-pin:hover {
  transform: scale(1.2);
}
</style>