<template>
  <div class="stations-view-split-layout">

    <div ref="mapContainer" class="map-canvas-panel"></div>

    <div class="station-inspector-panel" v-if="activeStation">

      <div class="inspector-header-box">
        <div class="flex items-center justify-between mb-2">
          <span class="inspector-station-code">{{ activeStation.station_code }}</span>
          <span :class="getStatusClass(activeStation.status)">
            {{ activeStation.status }}
          </span>
        </div>
        <h2 class="inspector-station-name">{{ activeStation.station_name }}</h2>
        <span class="inspector-location-desc">
          <strong>Site Notes:</strong> {{ activeStation.location_description || 'No location description logs registered for this observation point.' }}
        </span>
      </div>

      <div class="inspector-body-scroll">

        <div class="hardware-diagnostics-card">
          <h4 class="diagnostics-card-title">
            <i class="pi pi-compass text-slate-400"></i> Spatial Georeferencing
          </h4>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Latitude Coordinate</span>
            <span class="diagnostic-value text-slate-900">{{ activeStation.latitude?.toFixed(6) }}° N</span>
          </div>
          <div class="diagnostic-data-row">
            <span class="diagnostic-label">Longitude Coordinate</span>
            <span class="diagnostic-value text-slate-900">{{ activeStation.longitude?.toFixed(6) }}° E</span>
          </div>
        </div>

        <div class="hardware-diagnostics-card" v-if="activeSensor">
          <h4 class="diagnostics-card-title">
            <i class="pi pi-box text-slate-400"></i> Telemetry Sensor Asset
          </h4>
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
            <span class="diagnostic-value text-emerald-600">{{ activeSensor.calibration_offset?.toFixed(2) }}m</span>
          </div>
          <div class="diagnostic-data-row mt-2 pt-2 border-t border-slate-50">
            <span class="diagnostic-label">Node Battery Charge</span>
            <span class="flex items-center gap-1.5 font-bold" :class="activeSensor.battery_level < 20 ? 'text-rose-600' : 'text-slate-800'">
              <i class="pi" :class="activeSensor.battery_level < 20 ? 'pi-battery-down animate-pulse' : 'pi-battery-up text-emerald-500'"></i>
              {{ activeSensor.battery_level }}%
            </span>
          </div>
        </div>

        <div class="p-4 bg-amber-50/40 border border-amber-100 rounded-xl text-center text-xs text-amber-700 font-medium" v-else>
          <i class="pi pi-exclamation-triangle mr-1"></i> No hardware sensor profile linked to this station.
        </div>
      </div>

      <div class="inspector-action-footer">
        <router-link to="/analytics" class="pivot-analytics-btn">
          <i class="pi pi-chart-bar"></i>
          Inspect Aquifer Analytics Timeline
        </router-link>
      </div>

    </div>

    <div class="station-inspector-panel items-center justify-center p-8 text-center" v-else>
      <i class="pi pi-sliders-h text-slate-300 text-3xl"></i>
      <h3 class="text-sm font-bold text-slate-700 mt-3">No Station Highlighted</h3>
      <p class="text-xs text-slate-400 mt-1 max-w-[240px]">
        Select an observation well pinpoint from the map canvas to inspect hardware diagnostics.
      </p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import api from '../api';

// Core Leaflet Maps Requirements & Leaflet Stylesheet Bundle
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Separate Component Stylesheet Integration
import '../assets/styles/stations.css';

const mapContainer = ref(null);
let mapInstance = null;
const markersGroup = L.layerGroup();

const stations = ref([]);
const activeStation = ref(null);
const activeSensor = ref(null);

const initMapEngine = () => {
  if (!mapContainer.value) return;

  // Initializes Leaflet Map instance, centering natively around Kenya's general geographic baseline coordinates
  mapInstance = L.map(mapContainer.value, {
    zoomControl: false // Disables bulky default buttons to maintain a minimalist look
  }).setView([-1.286389, 36.817223], 7);

  // Add standard crisp, high-end vector map layers via an online provider tiles repository
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
  }).addTo(mapInstance);

  // Re-add customized fine-grained zoom utilities cleanly at the bottom right corner
  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);

  // Bind layers group container to the live map framework
  markersGroup.addTo(mapInstance);
};

const loadStationsFramework = async () => {
  try {
    const stationsResponse = await api.getStations();
    stations.value = stationsResponse.data;

    // Clear old map layers before re-plotting data arrays
    markersGroup.clearLayers();

    if (stations.value.length > 0) {
      const boundsArray = [];

      stations.value.forEach((station) => {
        if (station.latitude && station.longitude) {
          const latLng = [station.latitude, station.longitude];
          boundsArray.push(latLng);

          // Configure marker pin parameters
          const marker = L.marker(latLng, {
            icon: L.divIcon({
              className: 'custom-map-pin',
              html: `<div class="h-6 w-6 rounded-full bg-emerald-600 border-2 border-white flex items-center justify-center shadow-md animate-fade-in text-[10px] text-white font-bold">📍</div>`,
              iconSize: [24, 24],
              iconAnchor: [12, 12]
            })
          });

          // Bind click callbacks to fire details updates inside the dashboard right column panels
          marker.on('click', () => {
            inspectStation(station);
            mapInstance.panTo(latLng);
          });

          // Elegant mini hover popups drawn directly inside the map engine framework
          marker.bindPopup(`<b style="font-weight:700;color:#0f172a;">${station.station_code}</b><br><span style="font-size:11px;color:#64748b;">${station.station_name}</span>`);

          markersGroup.addLayer(marker);
        }
      });

      // Automatically adjust zoom frame variables to wrap all pins dynamically
      if (boundsArray.length > 0) {
        mapInstance.fitBounds(boundsArray, { padding: [50, 50] });
      }

      // Highlight the first well node automatically by default to ground the view layout layout
      inspectStation(stations.value[0]);
    }
  } catch (error) {
    console.error("Error pulling database coordinate layers:", error);
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
  if (status === 'active') return 'status-pill-active';
  if (status === 'maintenance') return 'status-pill-maintenance';
  return 'status-pill-inactive';
};

onMounted(async () => {
  initMapEngine();
  await nextTick(); // Ensures the wrapper template is rendered before loading spatial metrics
  await loadStationsFramework();
});
</script>