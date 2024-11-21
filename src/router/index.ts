import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import TimeDV from '@/views/TimeDV.vue'
import SpatialDV from '@/views/SpatialDV.vue'
import Sankey from '@/views/SpatialViews/Sankey.vue';      // Import the new component
import Cartogram from '@/views/SpatialViews/Cartogram.vue'; // Import the new component
import radarChart from '@/components/d3-charts/radarChart.vue'
import barChart from '@/components/d3-charts/barchart.vue'
import scatterPlot from '@/components/d3-charts/scatterPlot.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // {
    //   path: '/',
    //   name: 'home',
    //   component: HomeView 
    // },
    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue')
    // },
    {
      path: '/TimeDV',
      name: 'TimeDV',
      component: TimeDV,
      children: [
        {
          path: '/radar',
          name: 'radar',
          component: radarChart
        },
        {
          path: '/bar',
          name: 'bar',
          component: barChart
        },
        {
          path: '/scatter',
          name: 'scatter',
          component: scatterPlot
        }
      ]
    },
    {
      path: '/SpatialDV',
      name: 'SpatialDV',
      component: SpatialDV
    },
    {
      path: '/Cartogram',
      name: 'Cartogram',
      component: Cartogram
    },
    {
      path: '/Sankey',
      name: 'Sankey',
      component: Sankey
    },
  ]
})

export default router
