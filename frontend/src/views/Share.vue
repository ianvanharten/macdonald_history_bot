<template>
  <div class="share-page">
    <header class="share-header">
      <h1 class="title">A Conversation with Sir John A. Macdonald</h1>
    </header>

    <main class="main-content" v-if="!isLoading && !error">
      <div class="journal-entry">
        <div class="question-reference">
          <em>"{{ conversation.question }}"</em>
        </div>
        <div class="response-text" v-html="formattedAnswer"></div>
        <div class="signature">
          <span class="signature-line">—</span>
          <span class="signature-name">John A. Macdonald</span>
        </div>
        <div v-if="conversation.sources && conversation.sources.length > 0" class="sources-section">
          <h3>References</h3>
          <ul>
            <li v-for="(source, index) in conversation.sources" :key="index">
              {{ formatSourceName(source.source) }}, Parliament {{ source.parliament }}, Session {{ source.session }} — Page {{ source.page }} ({{ source.year }})
            </li>
          </ul>
        </div>
      </div>
    </main>

    <div v-if="isLoading" class="loading-state">
      <p>Loading conversation...</p>
    </div>

    <div v-if="error" class="error-state">
      <h2>Conversation Not Found</h2>
      <p>{{ error }}</p>
      <router-link to="/" class="home-link">Return to the main page</router-link>
    </div>

    <footer class="share-footer">
        <p>Shared from <router-link to="/" class="home-link">Ask Sir John A. Macdonald</router-link></p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

export default {
  name: 'Share',
  setup() {
    const route = useRoute()
    const conversation = ref(null)
    const isLoading = ref(true)
    const error = ref('')

    const md = new MarkdownIt({ html: true, breaks: true, linkify: true });

    onMounted(async () => {
      const shareId = route.params.shareId
      if (!shareId) {
        error.value = 'No share ID provided.'
        isLoading.value = false
        return
      }

      try {
        const result = await axios.get(`/api/share/${shareId}`)
        conversation.value = result.data
      } catch (err) {
        error.value = 'This shared conversation could not be found or has been removed.'
        console.error('Failed to fetch shared conversation:', err)
      } finally {
        isLoading.value = false
      }
    })

    const formattedAnswer = computed(() => {
        if (conversation.value && conversation.value.answer) {
            return md.render(conversation.value.answer);
        }
        return '';
    });

    const formatSourceName = (source) => {
      if (!source) return 'Unknown Source';
      return source
        .replace(/\.(pdf|json)$/i, '')
        .replace(/hansard_debate_/i, 'Hansard Debates ')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
    }

    return {
      conversation,
      isLoading,
      error,
      formattedAnswer,
      formatSourceName
    }
  }
}
</script>

<style scoped>
/* A simple, clean design for the shared page */
.share-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Georgia', serif;
  color: #333;
}
.share-header { text-align: center; margin-bottom: 2rem; }
.title { font-family: 'Cormorant Garamond', serif; font-size: 2.5rem; }
.main-content { background: #fdfdfd; border: 1px solid #eee; padding: 2rem; border-radius: 4px; }
.question-reference { font-style: italic; margin-bottom: 1.5rem; border-left: 3px solid #ccc; padding-left: 1rem; }
.response-text { line-height: 1.7; }
.signature { text-align: right; margin-top: 2rem; font-style: italic; }
.sources-section { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #eee; font-size: 0.9rem; }
.sources-section h3 { font-size: 1.2rem; }
.sources-section ul { list-style: disc; padding-left: 20px; }
.loading-state, .error-state { text-align: center; padding: 3rem; }
.error-state h2 { color: #8a2a2a; }
.home-link { color: #0056b3; text-decoration: none; }
.share-footer { text-align: center; margin-top: 2rem; font-size: 0.9rem; color: #777; }
</style>