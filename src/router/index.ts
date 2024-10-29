import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import TimeDV from '@/views/TimeDV.vue'
import SpatialDV from '@/views/SpatialDV.vue'

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
      component: TimeDV
    },
    {
      path: '/SpatialDV',
      name: 'SpatialDV',
      component: SpatialDV
    }
  ]
})

export default router
