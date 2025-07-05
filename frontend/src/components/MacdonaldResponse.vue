<template>
  <div class="macdonald-response" ref="responseContainer">
    <transition name="slide-fade" appear>
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
            <p v-for="(paragraph, index) in formattedParagraphs" :key="index" class="paragraph" v-html="paragraph">
            </p>
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
        <div class="loading-content">
          <div class="thinking-dots">
            <span>Sir John is carefully composing his response</span>
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
import MarkdownIt from 'markdown-it'

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
  setup(props) {
    // Initialize markdown parser
    const md = new MarkdownIt({
      html: true,
      breaks: true,
      linkify: true
    })

    const formattedDate = computed(() => {
      const now = new Date()
      return now.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    })

    const formattedParagraphs = computed(() => {
      if (!props.response || !props.response.answer) return []

      // Split on double line breaks first (standard paragraph breaks)
      let paragraphs = props.response.answer.split('\n\n')

      // If no double line breaks, try splitting on single line breaks
      if (paragraphs.length === 1) {
        paragraphs = props.response.answer.split('\n')
      }

      // If still one paragraph, try to split on sentence patterns for very long text
      if (paragraphs.length === 1 && paragraphs[0].length > 500) {
        // Split on periods followed by capital letters (new sentences that might be new thoughts)
        const text = paragraphs[0]
        const sentences = text.split(/\. (?=[A-Z])/)

        // Group sentences into paragraphs of reasonable length
        paragraphs = []
        let currentParagraph = ''

        sentences.forEach((sentence, index) => {
          if (index < sentences.length - 1) sentence += '.'

          if (currentParagraph.length + sentence.length > 400 && currentParagraph.length > 0) {
            paragraphs.push(currentParagraph.trim())
            currentParagraph = sentence + ' '
          } else {
            currentParagraph += sentence + ' '
          }
        })

        if (currentParagraph.trim()) {
          paragraphs.push(currentParagraph.trim())
        }
      }

      // Clean up paragraphs, filter out empty ones, and convert markdown to HTML
      return paragraphs
        .map(p => p.trim())
        .filter(p => p.length > 0)
        .map(p => md.renderInline(p)) // Convert markdown to HTML
    })

    return {
      formattedDate,
      formattedParagraphs
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
}

.paragraph {
  margin-bottom: 1.5rem;
  text-indent: 2rem;
}

.paragraph:last-child {
  margin-bottom: 0;
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

/* Simplified Loading State */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem;
  min-height: 200px;
}

.loading-journal {
  background: #fefefe;
  padding: 3rem;
  text-align: center;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.thinking-dots {
  font-family: 'EB Garamond', serif;
  font-size: 1.3rem;
  color: #666;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dots span {
  animation: dots 1.5s infinite;
  font-weight: bold;
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
    opacity: 0.3;
    transform: scale(1);
  }
  30% {
    opacity: 1;
    transform: scale(1.2);
  }
}

/* Enhanced Fade Animation */
.slide-fade-enter-active {
  transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.98);
}

.slide-fade-enter-to {
  opacity: 1;
  transform: translateY(0) scale(1);
}

@media (max-width: 768px) {
  .response-journal {
    padding: 2rem;
    margin: 1rem -10px;
  }

  .question-reference {
    font-size: 1.1rem;
  }

  .response-text {
    font-size: 1.25rem;
    line-height: 1.7;
  }

  .paragraph {
    text-indent: 1rem;
    margin-bottom: 1.25rem;
  }

  .signature-name {
    font-size: 1.1rem;
  }

  .loading-journal {
    padding: 2rem;
    margin: 0 -10px;
  }

  .thinking-dots {
    font-size: 1.1rem;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
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

  .paragraph {
    text-indent: 0.5rem;
  }
}
</style>