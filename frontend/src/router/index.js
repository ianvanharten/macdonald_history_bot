import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Sources from '../components/Sources.vue'
import Share from '../views/Share.vue' // Import the new component

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/sources',
    name: 'Sources',
    component: Sources
  },
  {
    path: '/c/:shareId', // Add the new route for shared conversations
    name: 'Share',
    component: Share
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router