<template>
  <div class="app-viewport">
    <!-- Top Global Header / Navbar (Hidden on Login) -->
    <Navbar
        v-if="!isAuthPage"
        :is-sidebar-open="isExpanded"
        @toggle-sidebar="handleSidebarToggle"
    />

    <div class="workspace-wrapper" :class="{ 'auth-workspace': isAuthPage }">
      <!-- Responsive Sidebar (Hidden on Login) -->
      <Sidebar
          v-if="!isAuthPage"
          :is-expanded="isExpanded"
          :is-mobile="isMobile"
          @toggle="handleSidebarToggle"
          @close="closeSidebarOnMobile"
      />

      <!-- Mobile Dimmed Backdrop Overlay (Hidden on Login) -->
      <transition name="backdrop-fade">
        <div
            v-if="!isAuthPage && isMobile && isExpanded"
            class="mobile-sidebar-backdrop"
            @click="closeSidebarOnMobile"
            aria-hidden="true"
        />
      </transition>

      <!-- Main Scrollable Work Area -->
      <main class="main-content-window" :class="{ 'sidebar-collapsed': !isExpanded && !isMobile, 'auth-content-window': isAuthPage }">
        <div :class="isAuthPage ? 'auth-container' : 'content-container'">
          <router-view v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from './components/Navbar.vue';
import Sidebar from './components/Sidebar.vue';
import './assets/styles/shell.css';

const route = useRoute();
const isExpanded = ref(true);
const isMobile = ref(false);

// Evaluates to true whenever the user is on the login page
const isAuthPage = computed(() => route.name === 'Login' || route.path === '/login');

// Breakpoint handler (1024px tablet/desktop boundary)
const checkScreenSize = () => {
  const mobileQuery = window.innerWidth <= 1024;
  isMobile.value = mobileQuery;

  // On mobile/tablet default to closed; on wide desktop default to open
  if (mobileQuery) {
    isExpanded.value = false;
  } else {
    isExpanded.value = true;
  }
};

const handleSidebarToggle = () => {
  isExpanded.value = !isExpanded.value;
};

const closeSidebarOnMobile = () => {
  if (isMobile.value) {
    isExpanded.value = false;
  }
};

// Auto-close mobile drawer whenever route changes
watch(() => route.path, () => {
  closeSidebarOnMobile();
});

onMounted(() => {
  checkScreenSize();
  window.addEventListener('resize', checkScreenSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize);
});
</script>

<style scoped>
/* Main Viewport Shell */
.app-viewport {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-canvas, #0b1320);
  color: var(--text-primary, #e2e8f0);
}

.workspace-wrapper {
  position: relative;
  display: flex;
  flex: 1;
  width: 100%;
  height: calc(100vh - 60px); /* Adjust based on navbar height */
  overflow: hidden;
}

/* Expands workspace to 100vh when on login */
.workspace-wrapper.auth-workspace {
  height: 100vh;
}

/* Scrollable Container for Dynamic Pages */
.main-content-window {
  flex: 1;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  background-color: var(--bg-surface, #dde1eb);
  transition: padding-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content-window.auth-content-window {
  background-color: transparent;
  padding: 0;
}

.content-container {
  width: 100%;
  max-width: 1600px; /* Prevents ultra-wide monitor stretching */
  margin: 0 auto;
  padding: 1rem;
  box-sizing: border-box;
}

.auth-container {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

@media (min-width: 768px) {
  .content-container {
    padding: 1.5rem 2rem;
  }
}

@media (min-width: 1440px) {
  .content-container {
    padding: 2rem 2.5rem;
  }
}

/* Mobile Backdrop */
.mobile-sidebar-backdrop {
  position: fixed;
  inset: 0;
  top: 60px; /* Below navbar */
  background-color: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(2px);
  z-index: 40; /* Sits right behind mobile drawer (z-index 50) */
}

/* Transitions */
.backdrop-fade-enter-active,
.backdrop-fade-leave-active {
  transition: opacity 0.2s ease;
}
.backdrop-fade-enter-from,
.backdrop-fade-leave-to {
  opacity: 0;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>