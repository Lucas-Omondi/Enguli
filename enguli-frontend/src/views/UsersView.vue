<template>
  <div class="users-view-wrapper">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="header-title">System User Directory</h1>
        <p class="header-subtitle">Manage access credentials, assign observer roles, and review account activity.</p>
      </div>

      <button
          v-if="authStore.canManageHardware"
          @click="showAddUserModal = true"
          class="action-btn primary-btn"
      >
        <i class="pi pi-user-plus text-xs"></i>
        <span>Add User</span>
      </button>
    </div>

    <!-- Summary Widgets -->
    <div class="summary-grid">
      <div class="summary-card">
        <span class="summary-label">Total Users</span>
        <span class="summary-value">{{ users.length }}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Admins & Engineers</span>
        <span class="summary-value text-sage">{{ adminCount }}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">Basin Observers / Farmers</span>
        <span class="summary-value text-amber">{{ farmerCount }}</span>
      </div>
    </div>

    <!-- Users Table Card -->
    <div class="data-card">
      <div v-if="loading" class="state-box">
        <i class="pi pi-spin pi-spinner text-sage text-2xl"></i>
        <p class="state-msg">Loading user directory...</p>
      </div>

      <div v-else-if="users.length > 0">
        <!-- Desktop Table -->
        <div class="table-container">
          <table class="users-table">
            <thead>
            <tr>
              <th>User / Name</th>
              <th>Username</th>
              <th>Assigned Role</th>
              <th>Email Contact</th>
              <th>Phone Number</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="u in users" :key="u.id" class="table-row">
              <td>
                <div class="user-cell">
                  <div class="avatar-circle">
                    {{ getInitials(u.first_name, u.last_name, u.username) }}
                  </div>
                  <div>
                    <div class="user-fullname">{{ u.first_name || u.last_name ? `${u.first_name} ${u.last_name}` : u.username }}</div>
                    <div class="user-subtext">ID: #{{ u.id }}</div>
                  </div>
                </div>
              </td>
              <td class="font-mono text-xs text-stone-700">@{{ u.username }}</td>
              <td>
                  <span :class="getRoleBadgeClass(u.profile?.role)">
                    {{ formatRoleName(u.profile?.role) }}
                  </span>
              </td>
              <td class="text-stone-600 text-xs">{{ u.email || '—' }}</td>
              <td class="text-stone-600 text-xs">{{ u.profile?.phone_number || '—' }}</td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="state-box">
        <i class="pi pi-users text-stone-400 text-2xl"></i>
        <p class="state-msg">No registered users found.</p>
      </div>
    </div>

    <!-- Modal: Add User -->
    <div v-if="showAddUserModal" class="modal-backdrop" @click.self="showAddUserModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">Create System User</h3>
          <button @click="showAddUserModal = false" class="modal-close-btn">&times;</button>
        </div>

        <form @submit.prevent="submitCreateUser" class="modal-form">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Username *</label>
              <input v-model="newUser.username" placeholder="e.g. jdoe" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Role *</label>
              <select v-model="newUser.role" required class="form-input">
                <option value="OBSERVER">Farmer / Observer</option>
                <option value="FIELD_ENGINEER">Field Engineer</option>
                <option value="ADMIN">System Administrator</option>
              </select>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">First Name</label>
              <input v-model="newUser.first_name" placeholder="John" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Last Name</label>
              <input v-model="newUser.last_name" placeholder="Doe" class="form-input" />
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Email Address</label>
              <input v-model="newUser.email" type="email" placeholder="john@example.com" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Phone Number</label>
              <input v-model="newUser.phone_number" placeholder="+254 700 000 000" class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Temporary Password *</label>
            <input v-model="newUser.password" type="password" placeholder="••••••••" required class="form-input" />
          </div>

          <div class="modal-actions">
            <button type="button" @click="showAddUserModal = false" class="btn-cancel">Cancel</button>
            <button type="submit" :disabled="isSubmitting" class="btn-submit">
              <i v-if="isSubmitting" class="pi pi-spin pi-spinner mr-1"></i>
              {{ isSubmitting ? 'Creating...' : 'Create Account' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const users = ref([]);
const loading = ref(true);
const showAddUserModal = ref(false);
const isSubmitting = ref(false);

const newUser = ref({
  username: '',
  password: '',
  email: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  role: 'OBSERVER'
});

const adminCount = computed(() => {
  return users.value.filter(u => u.profile?.role === 'ADMIN' || u.profile?.role === 'FIELD_ENGINEER').length;
});

const farmerCount = computed(() => {
  return users.value.filter(u => u.profile?.role === 'OBSERVER').length;
});

const loadUsers = async () => {
  loading.value = true;
  try {
    const res = await api.getUsers();
    users.value = res.data || [];
  } catch (error) {
    console.error("Failed to load user directory:", error);
  } finally {
    loading.value = false;
  }
};

const submitCreateUser = async () => {
  isSubmitting.value = true;
  try {
    await api.createUser(newUser.value);
    showAddUserModal.value = false;
    newUser.value = {
      username: '',
      password: '',
      email: '',
      first_name: '',
      last_name: '',
      phone_number: '',
      role: 'OBSERVER'
    };
    await loadUsers();
  } catch (error) {
    alert(error.response?.data?.detail || "Failed to create user. Verify that username is unique.");
  } finally {
    isSubmitting.value = false;
  }
};

const getInitials = (first, last, username) => {
  if (first && last) return `${first[0]}${last[0]}`.toUpperCase();
  if (username) return username.slice(0, 2).toUpperCase();
  return 'U';
};

const formatRoleName = (role) => {
  if (role === 'ADMIN') return 'Administrator';
  if (role === 'FIELD_ENGINEER') return 'Field Engineer';
  return 'Farmer / Observer';
};

const getRoleBadgeClass = (role) => {
  if (role === 'ADMIN') return 'role-badge badge-admin';
  if (role === 'FIELD_ENGINEER') return 'role-badge badge-engineer';
  return 'role-badge badge-farmer';
};

onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.users-view-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .page-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.header-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.02em;
  margin: 0;
}

.header-subtitle {
  font-size: 0.825rem;
  color: #78716c;
  margin: 0.25rem 0 0 0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.95rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  align-self: flex-start;
}

.primary-btn {
  background-color: #52796f;
  color: #ffffff;
}

.primary-btn:hover {
  background-color: #436b5f;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.summary-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  padding: 1rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: #8c857b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.summary-value {
  font-size: 1.45rem;
  font-weight: 700;
  color: #292524;
}

.text-sage {
  color: #385a50;
}

.text-amber {
  color: #8c5b24;
}

.data-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 10px;
  overflow: hidden;
}

.table-container {
  width: 100%;
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.users-table th {
  padding: 0.75rem 1rem;
  font-size: 0.68rem;
  font-weight: 700;
  color: #78716c;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background-color: #f7f6f4;
  border-bottom: 1px solid #eeeae4;
}

.table-row {
  border-bottom: 1px solid #f2eee8;
  transition: background-color 0.1s ease;
}

.table-row:hover {
  background-color: #f7f5f0;
}

.users-table td {
  padding: 0.8rem 1rem;
  font-size: 0.8rem;
  vertical-align: middle;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background-color: #eaf2ed;
  color: #385a50;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
}

.user-fullname {
  font-weight: 600;
  color: #292524;
}

.user-subtext {
  font-size: 0.65rem;
  color: #a8a29e;
}

.role-badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}

.badge-admin {
  background-color: #faebeb;
  color: #993838;
  border: 1px solid #f3d1d1;
}

.badge-engineer {
  background-color: #fcf4e8;
  color: #8c5b24;
  border: 1px solid #fae6cb;
}

.badge-farmer {
  background-color: #eaf2ed;
  color: #385a50;
  border: 1px solid #d1e2d7;
}

.state-box {
  padding: 2.5rem 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.state-msg {
  font-size: 0.78rem;
  color: #78716c;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-card {
  background-color: #fbfaf8;
  border: 1px solid #e7e3dc;
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid #eeeae4;
}

.modal-title {
  font-size: 1rem;
  font-weight: 700;
  color: #292524;
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.35rem;
  color: #a8a29e;
  cursor: pointer;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #78716c;
  text-transform: uppercase;
}

.form-input {
  width: 100%;
  padding: 0.55rem 0.75rem;
  background-color: #ffffff;
  border: 1px solid #ded9d2;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #292524;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #52796f;
}

.modal-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eeeae4;
}

.btn-cancel {
  padding: 0.5rem 0.85rem;
  background-color: #f2efe9;
  color: #6c665e;
  border: 1px solid #ded9d2;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit {
  padding: 0.5rem 1rem;
  background-color: #52796f;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background-color: #436b5f;
}
</style>