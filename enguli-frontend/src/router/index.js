import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import StationsView from '../views/StationsView.vue';
import AnalyticsView from '../views/AnalyticsView.vue';
import DataTablesView from '../views/DataTablesView.vue';
import LoginView from '../views/LoginView.vue';
import UsersView from '../views/UsersView.vue';
import AlertsView from '../views/AlertsView.vue';
import StorageModelView from "../views/StorageModelView.vue";
import ReportsView from "../views/ReportsView.vue";

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: LoginView,
        meta: { guestOnly: true }
    },
    {
        path: '/',
        name: 'Dashboard',
        component: DashboardView,
        meta: { requiresAuth: true }
    },
    {
        path: '/stations',
        name: 'Stations',
        component: StationsView,
        meta: { requiresAuth: true }
    },
    {
        path: '/analytics',
        name: 'Analytics',
        component: AnalyticsView,
        meta: { requiresAuth: true }
    },
    {
        path: '/tables',
        name: 'DataTables',
        component: DataTablesView,
        meta: { requiresAuth: true }
    },
    {
        path: '/users',
        name: 'Users',
        component: UsersView,
        meta: { requiresAuth: true }
    },
    {
        path: '/alerts',
        name: 'Alerts',
        component: AlertsView,
        meta: { requiresAuth: true }
    },
    {
        path: '/storage-model',
        name: 'StorageModel',
        component: StorageModelView,
        meta: { requiresAuth: true }
    },
    {
        path: '/reports',
        name: 'Reports',
        component: ReportsView,
        meta: { requiresAuth: true }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// Global Navigation Guard
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token');
    const isAuthenticated = !!token;

    if (to.meta.requiresAuth && !isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } });
    } else if (to.meta.guestOnly && isAuthenticated) {
        next({ name: 'Dashboard' });
    } else {
        next();
    }
});

export default router;