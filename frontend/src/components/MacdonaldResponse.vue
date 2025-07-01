<template>
  <div class="macdonald-response">
    <transition name="fade" appear>
      <div v-if="!isLoading" class="response-journal">
        <div class="journal-header">
          <div class="date-line">{{ formattedDate }}</div>
          <div class="ornamental-line"></div>
        </div>

        <div class="journal-content">
          <div class="question-reference">
            <em>"{{ response.question }}"</em>
          </div>

          <div class="response-text">
            {{ response.answer }}
          </div>

          <div class="signature">
            <span class="signature-line">—</span>
            <span class="signature-name">John A. Macdonald</span>
          </div>
        </div>

        <div class="journal-footer">
          <div class="ornamental-line"></div>
        </div>
      </div>
    </transition>

    <div v-if="isLoading" class="loading-state">
      <div class="loading-journal">
        <div class="loading-text">
          <div class="thinking-dots">
            <span>Sir John is reflecting</span>
            <span class="dots">
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'MacdonaldResponse',
  props: {
    response: {
      type: Object,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const formattedDate = computed(() => {
      const now = new Date()
      return now.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    })

    return {
      formattedDate
    }
  }
}
</script>

<style scoped>
.macdonald-response {
  margin: 2rem 0;
}

.response-journal {
  background: #fefefe;
  padding: 4rem;
  margin: 3rem 0;
  position: relative;
  background-image:
    linear-gradient(90deg, #f8f8f8 1px, transparent 1px),
    linear-gradient(180deg, #f8f8f8 1px, transparent 1px);
  background-size: 20px 20px;
  background-position: 0 0, 0 0;
}

.journal-header {
  text-align: center;
  margin-bottom: 2rem;
}

.date-line {
  font-family: 'EB Garamond', serif;
  font-size: 1.1rem;
  color: #666;
  font-style: italic;
  margin-bottom: 1rem;
}

.ornamental-line {
  width: 100px;
  height: 1px;
  background: #2c2c2c;
  margin: 0 auto;
  position: relative;
}

.ornamental-line::before,
.ornamental-line::after {
  content: '❦';
  position: absolute;
  top: -8px;
  font-size: 16px;
  color: #2c2c2c;
}

.ornamental-line::before {
  left: -15px;
}

.ornamental-line::after {
  right: -15px;
}

.journal-content {
  position: relative;
}

.question-reference {
  font-family: 'EB Garamond', serif;
  font-size: 1.2rem;
  color: #555;
  margin-bottom: 1.5rem;
  text-align: center;
  font-style: italic;
}

.response-text {
  font-family: 'EB Garamond', serif;
  font-size: 1.4rem;
  line-height: 1.8;
  color: #1a1a1a;
  text-align: justify;
  margin-bottom: 2rem;
  text-indent: 2rem;
}

.signature {
  text-align: right;
  margin-top: 2rem;
  font-family: 'EB Garamond', serif;
}

.signature-line {
  font-size: 1.5rem;
  margin-right: 0.5rem;
  color: #666;
}

.signature-name {
  font-size: 1.3rem;
  font-style: italic;
  color: #2c2c2c;
  font-weight: 500;
}

.journal-footer {
  margin-top: 2rem;
  text-align: center;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem;
}

.loading-journal {
  background: #fefefe;
  padding: 4rem;
  text-align: center;
}

.thinking-dots {
  font-family: 'EB Garamond', serif;
  font-size: 1.3rem;
  color: #666;
  font-style: italic;
}

.dots span {
  animation: dots 1.5s infinite;
}

.dots span:nth-child(1) {
  animation-delay: 0s;
}

.dots span:nth-child(2) {
  animation-delay: 0.5s;
}

.dots span:nth-child(3) {
  animation-delay: 1s;
}

@keyframes dots {
  0%, 60%, 100% {
    opacity: 0;
  }
  30% {
    opacity: 1;
  }
}

.fade-enter-active {
  transition: all 0.8s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-enter-to {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 768px) {
  .response-journal {
    padding: 2rem;
    margin: 1rem -10px;
  }

  .response-journal::before {
    transform: translate(2px, 2px);
  }

  .question-reference {
    font-size: 1.1rem;
  }

  .response-text {
    font-size: 1.25rem;
    line-height: 1.7;
    text-indent: 1rem;
  }

  .signature-name {
    font-size: 1.1rem;
  }

  .loading-journal {
    padding: 2rem;
    margin: 0 -10px;
  }
}

@media (max-width: 480px) {
  .response-journal {
    padding: 1.5rem;
    background-size: 15px 15px;
  }

  .response-text {
    font-size: 1.2rem;
    text-align: left;
  }
}
</style>