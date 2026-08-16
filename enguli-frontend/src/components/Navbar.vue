<template>
  <header class="navbar-strip">
    <!-- Left Section: Mobile Menu Trigger + Brand Identity -->
    <div class="nav-brand-group">
      <!-- Mobile / Tablet Hamburger Toggle Button -->
      <button
          type="button"
          class="sidebar-toggle-btn"
          @click="$emit('toggle-sidebar')"
          aria-label="Toggle Navigation Menu"
      >
        <svg
            v-if="!isSidebarOpen"
            xmlns="http://www.w3.org/2000/svg"
            class="icon-svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            class="icon-svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Logo Icon (Earthy Sage Tone) -->
      <div class="brand-badge">
        <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      </div>

      <!-- System Title -->
      <div class="brand-titles">
        <span class="brand-name">Enguli Platform</span>
        <span class="brand-subtitle">Groundwater Telemetry</span>
      </div>
    </div>

    <!-- Right Section: Status Indicator + User Profile -->
    <div class="nav-meta-group">
      <!-- Muted Live Telemetry Pill -->
      <div class="status-indicator-pill">
        <span class="pulse-beacon">
          <span class="beacon-wave"></span>
          <span class="beacon-core"></span>
        </span>
        <span class="status-label">Telemetry Active</span>
      </div>

      <div class="divider-vertical"></div>

      <!-- User Profile Badge (Muted Neutral Gray) -->
      <div class="user-profile-group">
        <div class="user-avatar" title="System Administrator">
          AD
        </div>
        <div class="user-meta hidden-mobile">
          <span class="user-name">Administrator</span>
          <span class="user-role">Enguli Sand River</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  isSidebarOpen: {
    type: Boolean,
    default: false
  }
});

defineEmits(['toggle-sidebar']);
</script>

<style scoped>
/* Top Navigation Bar: Soft Stone/Nude Balanced Background */
.navbar-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 62px;
  padding: 0 1.25rem;
  background-color: #f7f6f4; /* Warm neutral bone/nude tone */
  border-bottom: 1px solid #e7e4df;
  box-shadow: 0 1px 3px rgba(30, 41, 59, 0.03);
  box-sizing: border-box;
  z-index: 50;
  position: relative;
}

/* Brand Group */
.nav-brand-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Responsive Hamburger Toggle Button */
.sidebar-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #ded9d2;
  background-color: #f0ece6;
  color: #57534e;
  cursor: pointer;
  padding: 0;
  transition: all 0.15s ease;
}

.sidebar-toggle-btn:hover {
  background-color: #e6e0d8;
  color: #292524;
}

.icon-svg {
  width: 18px;
  height: 18px;
}

/* On Desktop screens > 1024px, hide the hamburger button */
@media (min-width: 1025px) {
  .sidebar-toggle-btn {
    display: none;
  }
}

/* Brand Icon (Muted Earthy Sage) */
.brand-badge {
  width: 32px;
  height: 32px;
  background-color: #52796f; /* Muted slate sage */
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fdfdfc;
  box-shadow: 0 1px 2px rgba(82, 121, 111, 0.2);
}

.brand-icon {
  width: 18px;
  height: 18px;
}

/* Brand Typography */
.brand-titles {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 0.925rem;
  font-weight: 600;
  color: #383533;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.brand-subtitle {
  font-size: 0.65rem;
  font-weight: 500;
  color: #8c857b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 1px;
}

/* Right Section Group */
.nav-meta-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Muted Status Pill */
.status-indicator-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background-color: #eeeae4;
  border: 1px solid #dfd9d0;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
}

.pulse-beacon {
  position: relative;
  display: flex;
  width: 8px;
  height: 8px;
}

.beacon-wave {
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background-color: #84a98c;
  opacity: 0.6;
  animation: pulsePing 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.beacon-core {
  position: relative;
  display: inline-flex;
  border-radius: 9999px;
  width: 8px;
  height: 8px;
  background-color: #52796f;
}

.status-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #57534e;
}

@keyframes pulsePing {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Divider */
.divider-vertical {
  width: 1px;
  height: 18px;
  background-color: #e0dad1;
}

/* User Profile */
.user-profile-group {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background-color: #6c665e;
  color: #f7f6f4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: #383533;
  line-height: 1.1;
}

.user-role {
  font-size: 0.65rem;
  color: #8c857b;
}

/* Responsive Hide Rules */
@media (max-width: 640px) {
  .status-label {
    display: none;
  }

  .status-indicator-pill {
    padding: 0.4rem;
  }

  .hidden-mobile {
    display: none;
  }

  .brand-subtitle {
    display: none;
  }
}
</style>