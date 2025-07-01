<template>
  <div class="app">
    <header class="header">
      <h1 class="title">Sir John A. Macdonald</h1>
      <p class="subtitle">Canada's First Prime Minister • Historical Conversations</p>
    </header>

    <main class="main-content">
      <div class="conversation-container">
        <QuestionInput
          @question-submitted="handleQuestionSubmitted"
          :is-loading="isLoading"
          :current-question="currentQuestion"
        />

        <div v-if="response" class="response-section">
          <MacdonaldResponse
            :response="response"
            :is-loading="isLoading"
          />

          <SourceQuotes
            v-if="response.sources && response.sources.length > 0"
            :sources="response.sources"
          />

          <FollowUpSuggestions
            v-if="response.follow_ups && response.follow_ups.length > 0"
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
import { ref } from 'vue'
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

    const handleQuestionSubmitted = async (question) => {
      currentQuestion.value = question
      isLoading.value = true
      error.value = ''
      response.value = null

      try {
        const result = await axios.post('http://localhost:8000/ask', {
          question: question
        })

        response.value = result.data
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
  padding: 3rem 0 4rem 0;
  margin-bottom: 3rem;
}

.title {
  font-family: 'EB Garamond', serif;
  font-size: clamp(2.5rem, 4vw, 3.5rem);
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
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
    font-size: 2.2rem;
  }

  .subtitle {
    font-size: 1rem;
  }
}
</style>