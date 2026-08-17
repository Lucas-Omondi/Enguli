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

    <!-- Right Section: Status Indicator + User Profile Dropdown -->
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

      <!-- User Profile Interactive Badge & Dropdown -->
      <div class="user-profile-wrapper" ref="dropdownRef">
        <button
            type="button"
            class="user-profile-trigger"
            @click="toggleDropdown"
            :aria-expanded="isDropdownOpen"
        >
          <div class="user-avatar" :title="displayName">
            {{ userInitials }}
          </div>
          <div class="user-meta hidden-mobile">
            <span class="user-name">{{ displayName }}</span>
            <span class="user-role">{{ authStore.roleDisplayName }}</span>
          </div>
          <i class="pi pi-chevron-down dropdown-caret" :class="{ 'caret-rotate': isDropdownOpen }"></i>
        </button>

        <!-- Profile / Logout Dropdown Menu -->
        <transition name="dropdown-fade">
          <div v-if="isDropdownOpen" class="user-dropdown-menu">
            <div class="dropdown-header">
              <span class="dropdown-username">@{{ authStore.user?.username || 'user' }}</span>
              <span class="dropdown-email">{{ authStore.user?.email || 'No email attached' }}</span>
            </div>

            <div class="dropdown-divider"></div>

            <router-link
                v-if="authStore.canManageHardware"
                to="/users"
                class="dropdown-item"
                @click="isDropdownOpen = false"
            >
              <i class="pi pi-users"></i>
              <span>User Directory</span>
            </router-link>

            <button type="button" class="dropdown-item logout-item" @click="handleLogout">
              <i class="pi pi-sign-out"></i>
              <span>Sign Out</span>
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

defineProps({
  isSidebarOpen: {
    type: Boolean,
    default: false
  }
});

defineEmits(['toggle-sidebar']);

const authStore = useAuthStore();
const router = useRouter();

const isDropdownOpen = ref(false);
const dropdownRef = ref(null);

const displayName = computed(() => {
  const u = authStore.user;
  if (!u) return 'Observer';
  if (u.first_name || u.last_name) {
    return `${u.first_name} ${u.last_name}`.trim();
  }
  return u.username;
});

const userInitials = computed(() => {
  const u = authStore.user;
  if (!u) return 'EP';
  if (u.first_name && u.last_name) {
    return `${u.first_name[0]}${u.last_name[0]}`.toUpperCase();
  }
  if (u.username) {
    return u.username.slice(0, 2).toUpperCase();
  }
  return 'EP';
});

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

const closeOnOutsideClick = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false;
  }
};

const handleLogout = () => {
  isDropdownOpen.value = false;
  authStore.logout();
  router.push('/login');
};

onMounted(() => {
  document.addEventListener('click', closeOnOutsideClick);
});

onUnmounted(() => {
  document.removeEventListener('click', closeOnOutsideClick);
});
</script>

<style scoped>
.navbar-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 62px;
  padding: 0 1.25rem;
  background-color: #f7f6f4;
  border-bottom: 1px solid #e7e4df;
  box-shadow: 0 1px 3px rgba(30, 41, 59, 0.03);
  box-sizing: border-box;
  z-index: 50;
  position: relative;
}

.nav-brand-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

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

@media (min-width: 1025px) {
  .sidebar-toggle-btn {
    display: none;
  }
}

.brand-badge {
  width: 32px;
  height: 32px;
  background-color: #52796f;
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

.nav-meta-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

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

.divider-vertical {
  width: 1px;
  height: 18px;
  background-color: #e0dad1;
}

/* User Profile Trigger & Dropdown */
.user-profile-wrapper {
  position: relative;
}

.user-profile-trigger {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.4rem;
  border-radius: 8px;
  transition: background-color 0.15s ease;
}

.user-profile-trigger:hover {
  background-color: #eeeae4;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background-color: #52796f;
  color: #fdfdfc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  box-shadow: 0 1px 2px rgba(82, 121, 111, 0.25);
}

.user-meta {
  display: flex;
  flex-direction: column;
  text-align: left;
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

.dropdown-caret {
  font-size: 0.65rem;
  color: #8c857b;
  transition: transform 0.2s ease;
}

.caret-rotate {
  transform: rotate(180deg);
}

/* Dropdown Menu Window */
.user-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 200px;
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(41, 37, 36, 0.08);
  padding: 0.5rem;
  z-index: 60;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dropdown-header {
  display: flex;
  flex-direction: column;
  padding: 0.4rem 0.6rem;
}

.dropdown-username {
  font-size: 0.78rem;
  font-weight: 700;
  color: #292524;
}

.dropdown-email {
  font-size: 0.68rem;
  color: #8c857b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-divider {
  height: 1px;
  background-color: #eeeae4;
  margin: 0.25rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  width: 100%;
  padding: 0.5rem 0.65rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  font-size: 0.76rem;
  font-weight: 500;
  color: #57534e;
  text-decoration: none;
  cursor: pointer;
  box-sizing: border-box;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background-color: #f0ece6;
  color: #292524;
}

.logout-item {
  color: #993838;
}

.logout-item:hover {
  background-color: #faebeb;
  color: #802626;
}

/* Transitions */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
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