import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import StationsView from '../views/StationsView.vue';
import AnalyticsView from '../views/AnalyticsView.vue';
import DataTablesView from '../views/DataTablesView.vue';

const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: DashboardView
    },
    {
        path: '/stations',
        name: 'Stations',
        component: StationsView
    },
    {
        path: '/analytics',
        name: 'Analytics',
        component: AnalyticsView
    },
    {
        path: '/tables',
        name: 'DataTables',
        component: DataTablesView
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;