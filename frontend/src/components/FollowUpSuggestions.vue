<template>
  <div class="follow-up-suggestions">
    <div class="suggestions-header">
      <h3>Continue the Conversation</h3>
      <p>You might also wish to inquire about:</p>
    </div>

    <div class="suggestions-list">
      <button
        v-for="(suggestion, index) in suggestions"
        :key="index"
        @click="handleSuggestionClick(suggestion)"
        class="suggestion-button"
      >
        <span class="suggestion-icon">❓</span>
        <span class="suggestion-text">{{ suggestion }}</span>
        <span class="suggestion-arrow">→</span>
      </button>
    </div>

    <div class="suggestions-footer">
      <p class="footer-note">
        Click any question above to continue your conversation with Sir John A. Macdonald
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FollowUpSuggestions',
  props: {
    suggestions: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  emits: ['suggestion-clicked'],
  setup(props, { emit }) {
    const handleSuggestionClick = (suggestion) => {
      emit('suggestion-clicked', suggestion)
    }

    return {
      handleSuggestionClick
    }
  }
}
</script>

<style scoped>
.follow-up-suggestions {
  margin-top: 3rem;
  background: #f8f8f8;
  padding: 3rem;
}

.suggestions-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.suggestions-header h3 {
  font-family: 'EB Garamond', serif;
  font-size: 1.6rem;
  font-weight: 600;
  color: #2c2c2c;
  margin-bottom: 0.5rem;
}

.suggestions-header p {
  font-size: 1.1rem;
  color: #666;
  font-style: italic;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.suggestion-button {
  background: #fff;
  border: none;
  padding: 1.5rem 2rem;
  text-align: left;
  cursor: pointer;
  font-family: 'Crimson Text', serif;
  font-size: 1.1rem;
  color: #2c2c2c;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.suggestion-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(44, 44, 44, 0.05), transparent);
  transition: left 0.5s ease;
}

.suggestion-button:hover::before {
  left: 100%;
}

.suggestion-button:hover {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
}

.suggestion-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.suggestion-icon {
  font-size: 1.2rem;
  color: #666;
  flex-shrink: 0;
}

.suggestion-text {
  flex: 1;
  line-height: 1.4;
  font-weight: 500;
}

.suggestion-arrow {
  font-size: 1.2rem;
  color: #999;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.suggestion-button:hover .suggestion-arrow {
  opacity: 1;
  transform: translateX(0);
  color: #2c2c2c;
}

.suggestions-footer {
  text-align: center;
  padding-top: 2rem;
}

.footer-note {
  font-size: 0.95rem;
  color: #888;
  font-style: italic;
}

@media (max-width: 768px) {
  .follow-up-suggestions {
    padding: 1.5rem;
    margin-top: 1.5rem;
  }

  .suggestions-header h3 {
    font-size: 1.4rem;
  }

  .suggestions-header p {
    font-size: 1rem;
  }

  .suggestion-button {
    padding: 1rem;
    font-size: 1rem;
    gap: 0.75rem;
  }

  .suggestion-icon {
    font-size: 1rem;
  }

  .suggestion-arrow {
    font-size: 1rem;
  }

  .footer-note {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .follow-up-suggestions {
    padding: 1rem;
    border-radius: 8px;
  }

  .suggestion-button {
    padding: 0.875rem;
    border-radius: 8px;
  }

  .suggestion-text {
    font-size: 0.95rem;
  }
}

/* Subtle animation for when suggestions appear */
.follow-up-suggestions {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Stagger animation for suggestion buttons */
.suggestion-button:nth-child(1) {
  animation: slideInLeft 0.5s ease-out 0.1s both;
}

.suggestion-button:nth-child(2) {
  animation: slideInLeft 0.5s ease-out 0.2s both;
}

.suggestion-button:nth-child(3) {
  animation: slideInLeft 0.5s ease-out 0.3s both;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>