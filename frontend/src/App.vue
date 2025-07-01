<template>
  <div class="app">
    <header class="header">
      <h1 class="title">Ask Sir John A. MacDonald</h1>
      <div class="header-image">
        <img src="/john-a-comic.png" alt="Sir John A. Macdonald" class="portrait" />
      </div>
      <p class="subtitle">Step into history and have a conversation with Canada's first Prime Minister. Ask Sir John A. MacDonald about Confederation, his political career, or the challenges of building a new nation. His responses are grounded in authentic historical documents and speeches from the 19th century.</p>
    </header>

    <main class="main-content">
      <div class="conversation-container">
        <QuestionInput
          @question-submitted="handleQuestionSubmitted"
          :is-loading="isLoading"
          :current-question="currentQuestion"
        />

        <div v-if="response || isLoading" class="response-section" ref="responseSection">
          <MacdonaldResponse
            :response="response"
            :is-loading="isLoading"
          />

          <SourceQuotes
            v-if="response && response.sources && response.sources.length > 0"
            :sources="response.sources"
          />

          <FollowUpSuggestions
            v-if="response && response.follow_ups && response.follow_ups.length > 0"
            :suggestions="response.follow_ups"
            @suggestion-clicked="handleSuggestionClicked"
          />
        </div>

        <div v-if="error" class="error-message">
          <p>{{ error }}</p>
        </div>
      </div>
    </main>

    <footer class="footer">
      <p>Responses based on historical documents and speeches from the 19th century</p>
    </footer>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import QuestionInput from './components/QuestionInput.vue'
import MacdonaldResponse from './components/MacdonaldResponse.vue'
import SourceQuotes from './components/SourceQuotes.vue'
import FollowUpSuggestions from './components/FollowUpSuggestions.vue'

export default {
  name: 'App',
  components: {
    QuestionInput,
    MacdonaldResponse,
    SourceQuotes,
    FollowUpSuggestions
  },
  setup() {
    const currentQuestion = ref('')
    const response = ref(null)
    const isLoading = ref(false)
    const error = ref('')
    const responseSection = ref(null)

    const scrollToResponse = () => {
      if (responseSection.value) {
        responseSection.value.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
          inline: 'nearest'
        })
      }
    }

    const handleQuestionSubmitted = async (question) => {
      currentQuestion.value = question
      isLoading.value = true
      error.value = ''
      response.value = null

      // Scroll to loading state after a brief delay
      await nextTick()
      setTimeout(() => {
        scrollToResponse()
      }, 100)

      try {
        const result = await axios.post('http://localhost:8000/ask', {
          question: question
        })

        response.value = result.data

        // Scroll to response after it loads
        await nextTick()
        setTimeout(() => {
          scrollToResponse()
        }, 200) // Small delay to allow fade animation to start

      } catch (err) {
        error.value = 'I apologize, but I am unable to respond at this moment. Please ensure the server is running and try again.'
        console.error('API Error:', err)
      } finally {
        isLoading.value = false
      }
    }

    const handleSuggestionClicked = (suggestion) => {
      handleQuestionSubmitted(suggestion)
    }

    return {
      currentQuestion,
      response,
      isLoading,
      error,
      responseSection,
      handleQuestionSubmitted,
      handleSuggestionClicked
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  text-align: center;
  padding: 2rem 0 1rem 0;
  margin-bottom: 0.5rem;
}

.title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(3rem, 4.5vw, 4.2rem);
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1.5rem;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.header-image {
  margin: 1.5rem 0;
  text-align: center;
}

.portrait {
  max-width: 200px;
  height: auto;
}

.subtitle {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin-top: 1.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
  font-style: italic;
}

.main-content {
  flex: 1;
  padding-bottom: 2rem;
}

.conversation-container {
  max-width: 900px;
  margin: 0 auto;
}

.response-section {
  margin-top: 2rem;
  scroll-margin-top: 2rem; /* Adds space above when scrolled to */
}

.error-message {
  background: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 2rem;
  text-align: center;
  color: #666;
  font-style: italic;
}

.footer {
  text-align: center;
  padding: 4rem 0;
  margin-top: 4rem;
  color: #888;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .app {
    padding: 0 15px;
  }

  .header {
    padding: 1.5rem 0;
  }

  .title {
    font-size: 2.5rem;
  }

  .portrait {
    max-width: 150px;
  }

  .subtitle {
    font-size: 1rem;
    max-width: 90%;
    padding: 0 1rem;
  }
}
</style>