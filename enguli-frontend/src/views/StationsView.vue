<template>
  <div class="stations-view-split-layout">
    <!-- Map Canvas Panel -->
    <div class="map-container-wrapper">
      <div ref="mapContainer" class="map-canvas-panel"></div>
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
          <h4 class="diagnostics-card-title">Telemetry Sensor Asset</h4>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Sensor Type</span>
            <span class="diagnostic-value capitalize">{{ activeSensor.sensor_type }}</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Hardware Serial Number</span>
            <span class="diagnostic-value font-mono">{{ activeSensor.serial_number }}</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Calibration Offset Height (H)</span>
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
          <i class="pi pi-info-circle mr-1"></i> No hardware sensor profile linked to this station.
        </div>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import api from '../api';

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const mapContainer = ref(null);
let mapInstance = null;
const markersGroup = L.layerGroup();

const stations = ref([]);
const activeStation = ref(null);
const activeSensor = ref(null);

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

  // Muted light tile map layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(mapInstance);

  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
  markersGroup.addTo(mapInstance);
};

const loadStationsFramework = async () => {
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

      if (boundsArray.length > 0) {
        mapInstance.fitBounds(boundsArray, { padding: [40, 40] });
      }

      inspectStation(stations.value[0]);
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

const getStatusClass = (status) => {
  const s = (status || '').toLowerCase();
  if (s === 'active') return 'status-pill status-pill-active';
  if (s === 'maintenance') return 'status-pill status-pill-maintenance';
  return 'status-pill status-pill-inactive';
};

onMounted(async () => {
  initMapEngine();
  await nextTick();
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
/* Split Layout: Column on mobile, Row on desktop */
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
  min-height: 280px;
  z-index: 10;
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

/* Header */
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

/* Scrollable Body */
.inspector-body-scroll {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  overflow-y: auto;
}

/* Diagnostics Cards */
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

/* Battery Indicators */
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

/* Empty Sensor Notification */
.empty-sensor-card {
  padding: 0.85rem;
  background-color: #fcf8f2;
  border: 1px solid #f2e6d5;
  border-radius: 8px;
  text-align: center;
  font-size: 0.72rem;
  color: #8c5b24;
  font-weight: 500;
}

/* Action Footer */
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

/* Status Pill */
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

/* Empty Panel */
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
</style>

<style>
/* Global Leaflet Marker Styles */
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