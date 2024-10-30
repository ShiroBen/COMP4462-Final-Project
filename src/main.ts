import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// we will use ElementPlus for webpage design, so remember to install it beforehand
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// import d3.js
import * as d3 from 'd3'

const app = createApp(App)

app.use(router)

// use d3 for visualization
app.use(d3)

// use ElementPlus in our project
app.use(ElementPlus)

app.mount('#app')
