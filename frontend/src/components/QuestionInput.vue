<template>
    <div class="question-input">
    <form @submit.prevent="submitQuestion" class="question-form">
      <div class="input-group">
        <textarea
          v-model="question"
          @keydown.enter.prevent="handleEnterKey"
          placeholder="What would you like to know about Canada's Confederation or my time as Prime Minister?"
          class="question-textarea"
          rows="3"
          :disabled="isLoading"
          required
        ></textarea>

        <div class="controls-row">
          <div class="model-selector">
            <label for="model-select" class="model-label">AI Model:</label>
            <select
              id="model-select"
              v-model="selectedModel"
              class="model-select"
              :disabled="isLoading"
            >
              <option value="google/gemini-2.0-flash-exp:free">Gemini 2.0 Flash (Recommended)</option>
              <option value="mistralai/mistral-small-3.2-24b-instruct:free">Mistral Small 3.2 24B</option>
              <option value="openrouter/cypher-alpha:free">OpenRouter Cypher Alpha</option>
            </select>
          </div>

          <button
            type="submit"
            class="submit-button"
            :disabled="isLoading || !question.trim()"
          >
            <span v-if="isLoading">Thinking...</span>
            <span v-else>Ask Question</span>
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'QuestionInput',
  props: {
    isLoading: {
      type: Boolean,
      default: false
    },
    currentQuestion: {
      type: String,
      default: ''
    }
  },
  emits: ['question-submitted'],
  setup(props, { emit }) {
    const question = ref('')
    const selectedModel = ref('google/gemini-2.0-flash-exp:free') // Default to Gemini

    // Watch for changes in currentQuestion to update the input when suggestions are clicked
    watch(() => props.currentQuestion, (newQuestion) => {
      if (newQuestion) {
        question.value = newQuestion
      }
    })

    const submitQuestion = () => {
      if (question.value.trim() && !props.isLoading) {
        emit('question-submitted', {
          question: question.value.trim(),
          model: selectedModel.value
        })
        question.value = '' // Clear the input after submission
      }
    }

    const handleEnterKey = (event) => {
      if (!event.shiftKey) {
        submitQuestion()
      }
    }

    return {
      question,
      selectedModel,
      submitQuestion,
      handleEnterKey
    }
  }
}
</script>

<style scoped>
.question-input {
  padding: 1rem 0;
  margin: 0.5rem 0;
}

.question-form {
  width: 100%;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.controls-row {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.model-selector {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.model-label {
  font-family: 'Crimson Text', serif;
  font-size: 0.95rem;
  color: #666;
  font-weight: 500;
}

.model-select {
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  font-family: 'Crimson Text', serif;
  font-size: 0.95rem;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.model-select:focus {
  outline: none;
  border-color: #2c2c2c;
  box-shadow: 0 2px 6px rgba(44, 44, 44, 0.1);
}

.model-select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

.question-textarea {
  width: 100%;
  padding: 1.5rem;
  border: none;
  background: #f0f8ff;
  font-family: 'Crimson Text', serif;
  font-size: 1.1rem;
  line-height: 1.6;
  resize: vertical;
  min-height: 120px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.question-textarea:focus {
  outline: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.question-textarea:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

.question-textarea::placeholder {
  color: #999;
  font-style: italic;
}

.submit-button {
  padding: 1rem 2.5rem;
  background: #2c2c2c;
  color: #fff;
  border: none;
  font-family: 'Crimson Text', serif;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
  border-radius: 8px;
  white-space: nowrap;
}

.submit-button:hover:not(:disabled) {
  background: #1a1a1a;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.submit-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.submit-button:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .question-input {
    padding: 1rem 0;
  }

  .controls-row {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .question-textarea {
    font-size: 1rem;
    min-height: 100px;
    padding: 1.25rem;
  }

  .submit-button {
    padding: 1rem 2rem;
    font-size: 1rem;
  }

  .model-select {
    font-size: 0.9rem;
  }
}
</style>