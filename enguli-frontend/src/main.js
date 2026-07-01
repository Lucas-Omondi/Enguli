import { createApp } from 'vue'
import App from './App.vue'
import router from './router';

// PrimeVue Core Configuration
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura'; // Ultra-modern premium theme
import 'primeicons/primeicons.css';       // Icon pack

// Global Tailwind Layout Styles
import './assets/tailwind.css';

const app = createApp(App);

app.use(router);
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.my-app-dark', // Allows manual toggle if needed
        }
    }
});

app.mount('#app');