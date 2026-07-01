<template>
  <nav class="navbar-strip">
    <div class="flex items-center space-x-3">
      <div class="h-8 w-8 bg-emerald-600 rounded-lg flex items-center justify-center shadow-sm shadow-emerald-200">
        <i class="pi pi-chart-line text-white text-sm"></i>
      </div>
      <div>
        <span class="text-sm font-semibold text-slate-900 tracking-tight block">Enguli Project</span>
        <span class="text-[10px] text-slate-400 font-medium tracking-wider uppercase block -mt-0.5">Groundwater Telemetry</span>
      </div>
    </div>

    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-100">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span class="text-xs font-medium text-slate-600">System Live</span>
      </div>
      <div class="h-4 w-px bg-slate-200"></div>
      <div class="flex items-center space-x-2.5">
        <div class="h-8 w-8 rounded-full bg-slate-900 flex items-center justify-center text-xs font-semibold text-white tracking-wider shadow-inner">
          AD
        </div>
        <span class="text-xs font-medium text-slate-700 hidden sm:block">Administrator</span>
      </div>
    </div>
  </nav>
</template>

<script setup>
import '../assets/styles/shell.css';
</script>