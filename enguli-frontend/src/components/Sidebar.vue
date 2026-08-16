<template>
  <aside
      class="sidebar-container"
      :class="[
      isExpanded ? 'sidebar-expanded' : 'sidebar-collapsed',
      { 'mobile-drawer-open': isMobile && isExpanded }
    ]"
  >
    <div class="sidebar-main-content">
      <!-- Section Header -->
      <div class="sidebar-header" :class="isExpanded ? 'justify-between' : 'justify-center'">
        <span v-if="isExpanded" class="sidebar-label">
          Navigation Hub
        </span>
        <button
            @click="toggleSidebar"
            class="sidebar-toggle-btn"
            :title="isExpanded ? 'Collapse Navigation' : 'Expand Navigation'"
        >
          <i :class="['pi text-xs transition-transform duration-200', isExpanded ? 'pi-chevron-left' : 'pi-chevron-right']"></i>
        </button>
      </div>

      <!-- Navigation Links List -->
      <nav class="sidebar-nav-list">
        <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="sidebar-nav-item"
            :class="isActive(item.path) ? 'nav-item-active' : 'nav-item-inactive'"
            :title="!isExpanded ? item.name : ''"
            @click="handleNavClick"
        >
          <div class="icon-wrapper">
            <i :class="[item.icon, 'nav-icon']"></i>
          </div>

          <span v-if="isExpanded" class="nav-text">
            {{ item.name }}
          </span>

          <!-- Subtle active indicator pill -->
          <span v-if="isExpanded && isActive(item.path)" class="active-dot"></span>
        </router-link>
      </nav>
    </div>

    <!-- Footer System Status (Warm Stone) -->
    <div class="sidebar-footer" :class="isExpanded ? 'justify-start gap-2.5' : 'justify-center'">
      <i class="pi pi-database footer-icon"></i>
      <div v-if="isExpanded" class="footer-meta">
        <span class="footer-title">Neon Database</span>
        <span class="footer-subtitle">Cloud Sync Active</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router';

const props = defineProps({
  isExpanded: {
    type: Boolean,
    required: true
  },
  isMobile: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['toggle', 'close']);

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

const handleNavClick = () => {
  if (props.isMobile) {
    emit('close');
  }
};

const isActive = (path) => {
  if (path === '/') return route.path === '/';
  return route.path.startsWith(path);
};
</script>

<style scoped>
/* Main Container: Muted warm stone surface */
.sidebar-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background-color: #f7f6f4;
  border-right: 1px solid #e7e4df;
  height: 100%;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1), transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
  flex-shrink: 0;
  z-index: 45;
}

/* Desktop Width States */
.sidebar-expanded {
  width: 240px;
}

.sidebar-collapsed {
  width: 68px;
}

/* Mobile Off-Canvas Drawer Behavior */
@media (max-width: 1024px) {
  .sidebar-container {
    position: fixed;
    top: 62px; /* Sits directly beneath top navbar */
    bottom: 0;
    left: 0;
    width: 260px;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.08);
    transform: translateX(-100%);
  }

  .sidebar-container.mobile-drawer-open {
    transform: translateX(0);
  }
}

/* Header */
.sidebar-header {
  display: flex;
  align-items: center;
  padding: 1rem 1rem 0.5rem 1.1rem;
  min-height: 42px;
}

.sidebar-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #8c857b;
  text-transform: uppercase;
}

.sidebar-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px solid #ded9d2;
  background-color: #f0ece6;
  color: #6c665e;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
}

.sidebar-toggle-btn:hover {
  background-color: #e5dfd7;
  color: #383533;
}

/* On mobile screen hide the inner collapse button since Navbar has hamburger */
@media (max-width: 1024px) {
  .sidebar-toggle-btn {
    display: none;
  }
}

/* Navigation List */
.sidebar-nav-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.6rem 0.65rem;
}

/* Navigation Items */
.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.84rem;
  font-weight: 500;
  transition: all 0.15s ease;
  white-space: nowrap;
  position: relative;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
}

.nav-icon {
  font-size: 0.95rem;
}

.nav-text {
  flex: 1;
}

/* Inactive State: Neutral warm stone text */
.nav-item-inactive {
  color: #6c665e;
}

.nav-item-inactive:hover {
  background-color: #ede8e1;
  color: #292524;
}

/* Active State: Soft muted sage & warm sand background */
.nav-item-active {
  background-color: #e5ede8;
  color: #385a50;
  font-weight: 600;
}

.nav-item-active .nav-icon {
  color: #436b5f;
}

.active-dot {
  width: 5px;
  height: 5px;
  border-radius: 9999px;
  background-color: #52796f;
}

/* Footer Section */
.sidebar-footer {
  display: flex;
  align-items: center;
  padding: 0.85rem 1rem;
  border-top: 1px solid #e7e4df;
  background-color: #f2efe9;
}

.footer-icon {
  font-size: 0.9rem;
  color: #52796f;
}

.footer-meta {
  display: flex;
  flex-direction: column;
}

.footer-title {
  font-size: 0.72rem;
  font-weight: 600;
  color: #44403c;
  line-height: 1.1;
}

.footer-subtitle {
  font-size: 0.62rem;
  color: #8c857b;
}
</style>