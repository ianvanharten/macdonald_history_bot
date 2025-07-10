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

          <!-- Follow-up question input -->
          <div v-if="response && !isLoading" class="follow-up-section">
            <h3 class="follow-up-title">Ask Another Question</h3>
            <QuestionInput
              @question-submitted="handleQuestionSubmitted"
              :is-loading="isLoading"
              :current-question="''"
              class="follow-up-input"
            />
          </div>
        </div>

        <div v-if="error" :class="['error-message', errorType]">
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

export default {
  name: 'App',
  components: {
    QuestionInput,
    MacdonaldResponse,
    SourceQuotes
  },
  setup() {
    const currentQuestion = ref('')
    const response = ref(null)
    const isLoading = ref(false)
    const error = ref('')
    const errorType = ref('')
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

    const handleQuestionSubmitted = async (data) => {
      // Handle both old format (string) and new format (object) for compatibility
      const question = typeof data === 'string' ? data : data.question
      const model = typeof data === 'string' ? 'google/gemini-2.0-flash-exp:free' : data.model

      currentQuestion.value = question
      isLoading.value = true
      error.value = ''
      errorType.value = ''
      response.value = null

      // Scroll to loading state after a brief delay
      await nextTick()
      setTimeout(() => {
        scrollToResponse()
      }, 100)

      try {
        const result = await axios.post('http://localhost:8000/ask', {
          question: question,
          model: model
        })

        // Check if the response contains an error field (backend-handled errors)
        if (result.data.error) {
          // Handle backend-reported errors
          const errorMessage = result.data.error.toLowerCase()

          if (errorMessage.includes('rate limit') || errorMessage.includes('429')) {
            error.value = `I apologize, but we've reached the usage limit for the AI model. Please wait a few minutes and try again.`
            errorType.value = 'rate-limit'
          } else if (errorMessage.includes('timeout') || errorMessage.includes('unavailable')) {
            error.value = 'The AI service is temporarily experiencing issues. Please try again in a moment.'
            errorType.value = 'server-error'
          } else if (errorMessage.includes('authentication') || errorMessage.includes('unauthorized')) {
            error.value = 'There seems to be an authentication issue with the AI service. Please contact support if this persists.'
            errorType.value = 'auth-error'
          } else {
            error.value = result.data.error
            errorType.value = 'general-error'
          }
          return // Exit early, don't set response.value
        }

        // If no error, process the successful response
        response.value = result.data

        // Scroll to response after it loads
        await nextTick()
        setTimeout(() => {
          scrollToResponse()
        }, 200) // Small delay to allow fade animation to start

      } catch (err) {
        // Handle HTTP-level errors (network issues, etc.)
        if (err.response?.status === 429 ||
            (err.response?.data?.error && err.response.data.error.includes('rate limit')) ||
            (err.message && err.message.includes('429'))) {
          error.value = `I apologize, but we've reached the usage limit for the AI model. Please wait a few minutes and try again.`
          errorType.value = 'rate-limit'
        } else if (err.response?.status >= 500) {
          error.value = 'The AI service is temporarily experiencing issues. Please try again in a moment.'
          errorType.value = 'server-error'
        } else if (err.response?.status === 401 || err.response?.status === 403) {
          error.value = 'There seems to be an authentication issue with the AI service. Please contact support if this persists.'
          errorType.value = 'auth-error'
        } else if (!navigator.onLine) {
          error.value = 'Please check your internet connection and try again.'
          errorType.value = 'network-error'
        } else {
          error.value = 'I apologize, but I am unable to respond at this moment. Please ensure the server is running and try again.'
          errorType.value = 'general-error'
        }
        console.error('API Error:', err)
      } finally {
        isLoading.value = false
      }
    }

    return {
      currentQuestion,
      response,
      isLoading,
      error,
      errorType,
      responseSection,
      handleQuestionSubmitted
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
  line-height: 1.5;
}

.error-message.rate-limit {
  background: #fff3cd;
  border-color: #ffeaa7;
  color: #856404;
}

.error-message.server-error {
  background: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.follow-up-section {
  margin-top: 3rem;
  padding: 2rem;
  background: #f8f8ff;
  border-radius: 12px;
  border-top: 3px solid #2c2c2c;
}

.follow-up-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  color: #2c2c2c;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: 600;
}

.follow-up-input {
  margin: 0;
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

  .follow-up-section {
    margin-top: 2rem;
    padding: 1.5rem;
  }

  .follow-up-title {
    font-size: 1.3rem;
  }
}
</style>