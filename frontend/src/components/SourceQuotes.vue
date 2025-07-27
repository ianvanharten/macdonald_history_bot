<template>
  <div class="source-quotes">
    <button
      @click="toggleExpanded"
      class="references-toggle"
      :class="{ expanded: isExpanded }"
    >
      <span class="toggle-icon">{{ isExpanded ? '▼' : '▶' }}</span>
      <span class="toggle-text">
        References ({{ sources.length }} {{ sources.length === 1 ? 'source' : 'sources' }})
      </span>
    </button>

    <transition name="expand">
      <div v-if="isExpanded" class="references-content">
        <div class="references-intro">
          <p>The following historical excerpts informed Sir John's response:</p>
        </div>

        <ul class="source-list">
          <li
            v-for="(source, index) in sources"
            :key="index"
            class="source-item"
          >
            <div class="source-citation">
              <span class="source-document">{{ formatSourceName(source.source) }}</span>
              <span class="source-details">
                Parliament {{ source.parliament }}, Session {{ source.session }} &mdash; Page {{ source.page }} ({{ source.year }})
              </span>
            </div>
          </li>
        </ul>

        <div class="references-footer">
          <p class="disclaimer">
            <em>For more on the historical sources used, go to the <router-link class="references-link" to="/sources">sources page</router-link>.</em>
          </p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'SourceQuotes',
  props: {
    sources: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup() {
    const isExpanded = ref(false)

    const toggleExpanded = () => {
      isExpanded.value = !isExpanded.value
    }

    const formatSourceName = (source) => {
      // Clean up the source name for display
      return source
        .replace(/\.(pdf|json)$/i, '')
        .replace(/hansard_debate_/i, 'Hansard Debates ')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
    }

    return {
      isExpanded,
      toggleExpanded,
      formatSourceName
    }
  }
}
</script>

<style scoped>
.source-quotes {
  margin-top: 3rem;
  background: #f8f8f8;
  overflow: hidden;
}

.references-toggle {
  width: 100%;
  background: #f8f8f8;
  border: none;
  padding: 1rem 1.5rem;
  text-align: left;
  cursor: pointer;
  font-family: 'Crimson Text', serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c2c2c;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.references-toggle:hover {
  background: #f0f0f0;
}

.references-toggle.expanded {
  background: #e8e8e8;
}

.toggle-icon {
  font-size: 0.9rem;
  color: #666;
  transition: transform 0.3s ease;
}

.toggle-text {
  flex: 1;
}

.references-content {
  padding: 1.5rem;
}

.references-intro {
  margin-bottom: 1.5rem;
  font-style: italic;
  color: #666;
  text-align: center;
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  list-style: none;
  padding-left: 0;
}

.source-item {
  border-left: 3px solid #ccc;
  padding: 0.5rem 1rem;
  background: #fff;
}

.source-citation {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.95rem;
  color: #666;
}

.source-document {
  font-weight: 600;
  color: #2c2c2c;
}

.source-details {
  font-style: italic;
}

.references-footer {
  margin-top: 2rem;
  padding-top: 2rem;
  text-align: center;
}

a.references-link {
  color: #2c2c2c;
}

.disclaimer {
  font-size: 0.9rem;
  color: #888;
}

.expand-enter-active, .expand-leave-active {
  transition: all 0.4s ease;
  overflow: hidden;
}

.expand-enter-from, .expand-leave-to {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.expand-enter-to, .expand-leave-from {
  max-height: 1000px;
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .references-toggle {
    padding: 1rem;
    font-size: 1rem;
  }

  .references-content {
    padding: 1rem;
  }

  .source-item {
    padding: 1rem;
    padding-left: 1rem;
    border-left-width: 3px;
  }

  .source-citation {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .source-citation {
    flex-direction: column;
    gap: 0.1rem;
  }
}
</style>