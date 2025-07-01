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

        <button
          type="submit"
          class="submit-button"
          :disabled="isLoading || !question.trim()"
        >
          <span v-if="isLoading">Thinking...</span>
          <span v-else>Ask Question</span>
        </button>
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

    // Watch for changes in currentQuestion to update the input when suggestions are clicked
    watch(() => props.currentQuestion, (newQuestion) => {
      if (newQuestion) {
        question.value = newQuestion
      }
    })

    const submitQuestion = () => {
      if (question.value.trim() && !props.isLoading) {
        emit('question-submitted', question.value.trim())
        // Don't clear the question here - let the parent handle it
      }
    }

    const handleEnterKey = (event) => {
      if (!event.shiftKey) {
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
  align-self: flex-end;
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
    align-self: stretch;
  }
}
</style>