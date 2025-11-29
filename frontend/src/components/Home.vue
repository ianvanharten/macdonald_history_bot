<template>
  <div class="home-page">
    <header class="header">
      <h1 class="title">Ask Sir John A. Macdonald</h1>
      <p class="subtitle">Watch an interview with the chatbot that brings Canada's first Prime Minister to life through authentic historical documents and speeches from the 19th century.</p>
    </header>

    <main class="main-content">
      <div class="video-container">
        <div class="video-wrapper">
          <iframe
            :src="youtubeEmbedUrl"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            class="youtube-embed"
          ></iframe>
        </div>
      </div>
    </main>

    <footer class="footer">
      <p>Responses were generated from <router-link to="/sources" class="footer-link">historical documents and speeches from the 19th century.</router-link></p>
      <br />
      <p class="creator-credit"><a href="https://longformnorth.com" class="footer-link">Longform North</a></p>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'Home',
  setup() {
    // Replace 'YOUR_VIDEO_ID' with your actual YouTube video ID
    // For example, if your URL is https://www.youtube.com/watch?v=dQw4w9WgXcQ
    // Then the video ID is: dQw4w9WgXcQ
    const videoId = '9t59eNbpj4A'

    const youtubeEmbedUrl = computed(() => {
      return `https://www.youtube.com/embed/${videoId}`
    })

    return {
      youtubeEmbedUrl
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  text-align: center;
  padding: 1.5rem 0 0.5rem 0;
  margin-bottom: 0;
}

.title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.5rem, 3.5vw, 3.2rem);
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1rem;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin-top: 0.75rem;
  margin-bottom: 1.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
  font-style: italic;
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 0;
  margin-top: 0;
}

.video-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  margin-top: 0;
}

.video-wrapper {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
  height: 0;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.youtube-embed {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.footer {
  text-align: center;
  padding: 1.5rem 0 1rem 0;
  margin-top: 1.5rem;
  color: #888;
  font-size: 1rem;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.footer-link {
  color: #666;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #2c2c2c;
}

.creator-credit {
  margin-top: 0.5rem;
  font-size: 1rem;
  color: #999;
}

@media (max-width: 768px) {
  .home-page {
    padding: 0 15px;
  }

  .header {
    padding: 1.5rem 0;
  }

  .title {
    font-size: 2rem;
  }

  .portrait {
    max-width: 150px;
  }

  .subtitle {
    font-size: 1rem;
    max-width: 90%;
    padding: 0 1rem;
  }

  .video-container {
    padding: 0 1rem;
  }
}
</style>