import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// we will use ElementPlus for webpage design, so remember to install it beforehand
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(router)


// use ElementPlus in our project
app.use(ElementPlus)

app.mount('#app')
