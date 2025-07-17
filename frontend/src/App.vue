<template>
  <div id="app">
    <nav class="navigation">
      <div class="nav-container">
        <div class="nav-brand">
          <router-link to="/" class="brand-link">
            <span class="brand-text">Ask Sir John A. MacDonald</span>
          </router-link>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link" :class="{ active: $route.name === 'Home' }">
            Chat
          </router-link>
          <router-link to="/sources" class="nav-link" :class="{ active: $route.name === 'Sources' }">
            Sources
          </router-link>
        </div>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Crimson Text', serif;
  background-color: #fdfdfb;
  color: #333;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navigation {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #2c2c2c;
}

.brand-text {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c2c2c;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #666;
  font-size: 1.1rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
  position: relative;
}

.nav-link:hover {
  color: #2c2c2c;
  background-color: #f8f8f8;
}

.nav-link.active {
  color: #2c2c2c;
  background-color: #f0f8ff;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background-color: #2c2c2c;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 15px;
    height: 60px;
  }

  .brand-text {
    font-size: 1.3rem;
  }

  .nav-links {
    gap: 1rem;
  }

  .nav-link {
    font-size: 1rem;
    padding: 0.4rem 0.8rem;
  }
}

@media (max-width: 480px) {
  .brand-text {
    font-size: 1.1rem;
  }
}
</style>