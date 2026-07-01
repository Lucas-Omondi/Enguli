<template>
  <aside :class="['sidebar-container', isExpanded ? 'sidebar-expanded' : 'sidebar-collapsed']">

    <div>
      <div :class="['sidebar-toggle-header', isExpanded ? 'justify-between' : 'justify-center']">
        <span v-if="isExpanded" class="text-[10px] font-bold tracking-wider text-slate-500 uppercase">
          Navigation Hub
        </span>
        <button @click="toggleSidebar" class="nav-trigger-action-btn" title="Toggle Navigation">
          <i :class="['pi text-sm transition-transform duration-300', isExpanded ? 'pi-times rotate-90' : 'pi-bars']"></i>
        </button>
      </div>

      <div class="p-2 space-y-1.5">
        <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="sidebar-menu-btn"
            :class="isActive(item.path) ? 'sidebar-btn-active' : 'sidebar-btn-inactive'"
            :title="!isExpanded ? item.name : ''"
        >
          <i :class="[item.icon, 'text-base shrink-0']"></i>

          <span v-if="isExpanded" class="sidebar-link-text">
            {{ item.name }}
          </span>
        </router-link>
      </div>
    </div>

    <div class="p-4 border-t border-slate-900/60 bg-slate-950/40 flex items-center" :class="isExpanded ? 'justify-start space-x-3' : 'justify-center'">
      <i class="pi pi-database text-slate-600 text-sm"></i>
      <span v-if="isExpanded" class="text-xs text-slate-500 font-medium whitespace-nowrap">PostgreSQL Connected</span>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router';

// Define the state tracking props sent from parent container adjustments
defineProps({
  isExpanded: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['toggle']);

const route = useRoute();

const navItems = [
  { name: 'Dashboard Overview', path: '/', icon: 'pi pi-th-large' },
  { name: 'Telemetry Stations', path: '/stations', icon: 'pi pi-map-marker' },
  { name: 'Hydrological Analytics', path: '/analytics', icon: 'pi pi-chart-bar' },
  { name: 'System Logs Table', path: '/tables', icon: 'pi pi-server' }
];

const toggleSidebar = () => {
  emit('toggle');
};

const isActive = (path) => {
  if (path === '/') return route.path === '/';
  return route.path.startsWith(path);
};
</script>