import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

// Import D3 correctly
import * as d3 from 'd3';

const app = createApp(App);

app.use(router);
app.use(ElementPlus);

app.mount('#app');