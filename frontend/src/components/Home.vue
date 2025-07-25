<template>
  <div class="home-page">
    <header class="header">
      <h1 class="title">Ask Sir John A. MacDonald</h1>
      <div class="header-image">
        <img src="/john-a-comic.png" alt="Sir John A. Macdonald" class="portrait" />
      </div>
      <p class="subtitle">Step into history and have a conversation with Canada's first Prime Minister. Ask Sir John A. MacDonald about Confederation, his political career, or the challenges of building a new nation. His responses are grounded in authentic historical documents and speeches from the 19th century.</p>
    </header>

    <main class="main-content">
      <div class="conversation-container">
        <!-- Render all previous Q&A pairs -->
        <div v-for="(pair, index) in conversationHistory" :key="index" class="conversation-pair">
          <QuestionInput
            :question-text="pair.question"
            :is-disabled="true"
            :is-loading="false"
            :current-question="pair.question"
            :show-submit-button="false"
          />

          <div v-if="pair.response || pair.isLoading" class="response-section">
            <MacdonaldResponse
              :response="pair.response"
              :is-loading="pair.isLoading"
            />

            <SourceQuotes
              v-if="pair.response && pair.response.sources && pair.response.sources.length > 0"
              :sources="pair.response.sources"
            />
          </div>

          <div v-if="pair.error" :class="['error-message', pair.errorType]">
            <p>{{ pair.error }}</p>
          </div>
        </div>

        <!-- Current active question input (only if under 3 questions) -->
        <div v-if="conversationHistory.length < 3" ref="activeInputSection">
          <h3 v-if="conversationHistory.length > 0" class="follow-up-title">Ask Another Question</h3>
          <QuestionInput
            @question-submitted="handleQuestionSubmitted"
            :is-loading="isLoading"
            :current-question="''"
            :is-disabled="false"
          />
        </div>
      </div>
    </main>

    <footer class="footer">
      <p>Responses based on <router-link to="/sources" class="footer-link">historical documents</router-link> and speeches from the 19th century</p>
      <p class="creator-credit">Created by Ian Van Harten</p>
    </footer>
  </div>
</template>

<script>
import { ref, reactive, nextTick } from 'vue'
import axios from 'axios'
import QuestionInput from './QuestionInput.vue'
import MacdonaldResponse from './MacdonaldResponse.vue'
import SourceQuotes from './SourceQuotes.vue'

export default {
  name: 'Home',
  components: {
    QuestionInput,
    MacdonaldResponse,
    SourceQuotes
  },
  setup() {
    const currentQuestion = ref('')
    const isLoading = ref(false)
    const conversationHistory = reactive([])
    const activeInputSection = ref(null)

    const scrollToResponse = () => {
      nextTick(() => {
        setTimeout(() => {
          if (activeInputSection.value) {
            // Scroll to just below the input section, showing the start of the response
            const inputRect = activeInputSection.value.getBoundingClientRect()
            const scrollTarget = window.pageYOffset + inputRect.bottom + 20 // 20px padding

            window.scrollTo({
              top: scrollTarget,
              behavior: 'smooth'
            })
          }
        }, 100)
      })
    }

    const handleQuestionSubmitted = async (data) => {
      // Handle both old format (string) and new format (object) for compatibility
      const question = typeof data === 'string' ? data : data.question

      // Don't allow more than 3 questions
      if (conversationHistory.length >= 3) {
        return
      }

      // Clear currentQuestion so the next input will be empty
      currentQuestion.value = ''
      isLoading.value = true

      // Add new conversation pair
      const newPair = {
        question: question,
        response: null,
        isLoading: true,
        error: '',
        errorType: ''
      }
      conversationHistory.push(newPair)

      // Scroll to show the start of where the response will appear
      scrollToResponse()

      try {
        const result = await axios.post('http://localhost:8000/ask', {
          question: question
        })

        // Check if the response contains an error field (backend-handled errors)
        if (result.data.error) {
          // Handle backend-reported errors
          const errorMessage = result.data.error.toLowerCase()

          if (errorMessage.includes('rate limit') || errorMessage.includes('429')) {
            newPair.error = `I apologize, but we've reached the usage limit for the AI model. Please wait a few minutes and try again.`
            newPair.errorType = 'rate-limit'
          } else if (errorMessage.includes('timeout') || errorMessage.includes('unavailable')) {
            newPair.error = 'The AI service is temporarily experiencing issues. Please try again in a moment.'
            newPair.errorType = 'server-error'
          } else if (errorMessage.includes('authentication') || errorMessage.includes('unauthorized')) {
            newPair.error = 'There seems to be an authentication issue with the AI service. Please contact support if this persists.'
            newPair.errorType = 'auth-error'
          } else {
            newPair.error = result.data.error
            newPair.errorType = 'general-error'
          }
        } else {
          // If no error, process the successful response
          newPair.response = result.data
        }

      } catch (err) {
        // Handle HTTP-level errors (network issues, etc.)
        if (err.response?.status === 429 ||
            (err.response?.data?.error && err.response.data.error.includes('rate limit')) ||
            (err.message && err.message.includes('429'))) {
          newPair.error = `I apologize, but we've reached the usage limit for the AI model. Please wait a few minutes and try again.`
          newPair.errorType = 'rate-limit'
        } else if (err.response?.status >= 500) {
          newPair.error = 'The AI service is temporarily experiencing issues. Please try again in a moment.'
          newPair.errorType = 'server-error'
        } else if (err.response?.status === 401 || err.response?.status === 403) {
          newPair.error = 'There seems to be an authentication issue with the AI service. Please contact support if this persists.'
          newPair.errorType = 'auth-error'
        } else if (!navigator.onLine) {
          newPair.error = 'Please check your internet connection and try again.'
          newPair.errorType = 'network-error'
        } else {
          newPair.error = 'I apologize, but I am unable to respond at this moment. Please ensure the server is running and try again.'
          newPair.errorType = 'general-error'
        }
        console.error('API Error:', err)
      } finally {
        newPair.isLoading = false
        isLoading.value = false
      }
    }

    return {
      currentQuestion,
      isLoading,
      conversationHistory,
      activeInputSection,
      handleQuestionSubmitted
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
  padding: 2rem 0 1rem 0;
  margin-bottom: 0.5rem;
}

.title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.5rem, 3.5vw, 3.2rem);
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

.conversation-pair {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}

.conversation-pair:last-child {
  border-bottom: none;
}

.response-section {
  margin-top: 2rem;
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

.follow-up-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  color: #2c2c2c;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: 600;
  margin-top: 2rem;
}

.footer {
  text-align: center;
  padding: 4rem 0;
  margin-top: 4rem;
  color: #888;
  font-size: 0.9rem;
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
  font-size: 0.85rem;
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

  .follow-up-title {
    font-size: 1.3rem;
  }
}
</style>