<template>
  <div class="app-viewport">
    <Navbar />

    <div class="workspace-wrapper">
      <Sidebar :is-expanded="isExpanded" @toggle="handleSidebarToggle" />

      <main class="main-content-window">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Navbar from './components/Navbar.vue';
import Sidebar from './components/Sidebar.vue';
import './assets/styles/shell.css';

const isExpanded = ref(true);

const handleSidebarToggle = () => {
  isExpanded.value = !isExpanded.value;
};
</script>

<style>
/* Clean workspace layout blend fade transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>