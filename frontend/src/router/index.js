import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Sources from '../components/Sources.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router