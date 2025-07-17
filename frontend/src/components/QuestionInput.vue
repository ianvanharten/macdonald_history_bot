<template>
    <div class="question-input">
    <form @submit.prevent="submitQuestion" class="question-form">
      <div class="input-group">
        <textarea
          v-model="question"
          @keydown.enter.prevent="handleEnterKey"
          placeholder="What would you like to know about Canada's Confederation or my time as Prime Minister?"
          class="question-textarea"
          :class="{ 'disabled': isDisabled }"
          rows="3"
          :disabled="isLoading || isDisabled"
          :required="!isDisabled"
        ></textarea>

        <div v-if="showSubmitButton" class="controls-row">
          <button
            type="submit"
            class="submit-button"
            :disabled="isLoading || !question.trim() || isDisabled"
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
    },
    questionText: {
      type: String,
      default: ''
    },
    isDisabled: {
      type: Boolean,
      default: false
    },
    showSubmitButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['question-submitted'],
  setup(props, { emit }) {
    const question = ref('')
    // Hardcoded model - using Google Gemini 2.0 Flash
    const model = 'google/gemini-2.0-flash-exp:free'

    // Watch for changes in currentQuestion to update the input when suggestions are clicked
    watch(() => props.currentQuestion, (newQuestion) => {
      if (newQuestion) {
        question.value = newQuestion
      }
    })

    // Watch for questionText prop to set pre-filled text for disabled inputs
    watch(() => props.questionText, (newText) => {
      if (newText) {
        question.value = newText
      }
    }, { immediate: true })

    const submitQuestion = () => {
      if (question.value.trim() && !props.isLoading && !props.isDisabled) {
        emit('question-submitted', {
          question: question.value.trim(),
          model: model
        })
        question.value = '' // Clear the input after submission
      }
    }

    const handleEnterKey = (event) => {
      if (!event.shiftKey && !props.isDisabled) {
        submitQuestion()
      }
    }

    return {
      question,
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
  justify-content: center;
  align-items: center;
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

.question-textarea.disabled {
  background-color: #f8f8f8;
  color: #666;
  cursor: default;
  opacity: 0.8;
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

  .question-textarea {
    font-size: 1rem;
    min-height: 100px;
    padding: 1.25rem;
  }

  .submit-button {
    padding: 1rem 2rem;
    font-size: 1rem;
  }
}
</style>