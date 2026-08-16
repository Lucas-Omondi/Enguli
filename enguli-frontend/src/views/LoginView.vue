<template>
  <div class="login-viewport">
    <div class="login-card">

      <!-- Brand Header -->
      <div class="login-brand-header">
        <div class="brand-badge">
          <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <h1 class="brand-title">Enguli Telemetry</h1>
        <p class="brand-desc">Sign in to access groundwater basin operations and monitoring telemetry.</p>
      </div>

      <!-- Error Alert -->
      <div v-if="authStore.authError" class="auth-error-banner">
        <i class="pi pi-exclamation-circle"></i>
        <span>{{ authStore.authError }}</span>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label" for="username">Username</label>
          <div class="input-wrapper">
            <i class="pi pi-user input-icon"></i>
            <input
                id="username"
                v-model="username"
                type="text"
                placeholder="Enter your username"
                required
                autocomplete="username"
                class="form-input"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <div class="input-wrapper">
            <i class="pi pi-lock input-icon"></i>
            <input
                id="password"
                v-model="password"
                type="password"
                placeholder="••••••••"
                required
                autocomplete="current-password"
                class="form-input"
            />
          </div>
        </div>

        <button
            type="submit"
            class="login-btn"
            :disabled="authStore.isLoading"
        >
          <i v-if="authStore.isLoading" class="pi pi-spin pi-spinner mr-2"></i>
          <span>{{ authStore.isLoading ? 'Authenticating...' : 'Sign In to Dashboard' }}</span>
        </button>
      </form>

      <!-- Footer Info -->
      <div class="login-card-footer">
        <span>Restricted Access: System Administrator & Basin Observers</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const username = ref('');
const password = ref('');

const handleLogin = async () => {
  try {
    await authStore.login(username.value, password.value);
    const redirectPath = route.query.redirect || '/';
    router.push(redirectPath);
  } catch (err) {
    // Auth error handled in store
  }
};
</script>

<style scoped>
.login-viewport {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f2efe9;
  padding: 1.25rem;
  box-sizing: border-box;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 12px;
  padding: 2rem 1.75rem;
  box-shadow: 0 4px 16px rgba(41, 37, 36, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.login-brand-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.brand-badge {
  width: 42px;
  height: 42px;
  background-color: #52796f;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fdfdfc;
  margin-bottom: 0.75rem;
}

.brand-icon {
  width: 22px;
  height: 22px;
}

.brand-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.02em;
  margin: 0;
}

.brand-desc {
  font-size: 0.78rem;
  color: #78716c;
  margin: 0.35rem 0 0 0;
  line-height: 1.4;
}

.auth-error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  background-color: #faebeb;
  border: 1px solid #f3d1d1;
  color: #993838;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 0.85rem;
  color: #a8a29e;
  font-size: 0.85rem;
}

.form-input {
  width: 100%;
  padding: 0.6rem 0.85rem 0.6rem 2.4rem;
  background-color: #ffffff;
  border: 1px solid #ded9d2;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #292524;
  outline: none;
  transition: border-color 0.15s ease;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #52796f;
}

.login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.7rem;
  background-color: #52796f;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease;
  margin-top: 0.25rem;
}

.login-btn:hover:not(:disabled) {
  background-color: #436b5f;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-card-footer {
  text-align: center;
  font-size: 0.68rem;
  color: #8c857b;
  border-top: 1px solid #eeeae4;
  padding-top: 0.85rem;
}
</style>