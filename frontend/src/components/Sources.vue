<template>
  <div class="sources-page">
    <header class="header">
      <h1 class="title">Historical Sources</h1>
      <p class="subtitle">
        Sir John A. MacDonald's responses are grounded in authentic historical documents and speeches from the 19th century.
        This page provides details about the primary sources used to create his knowledge base.
      </p>
    </header>

    <footer class="footer">
      <p>Historical accuracy maintained through authentic 19th-century documents and records</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'Sources'
}
</script>

<style scoped>
.sources-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  text-align: center;
  padding: 2rem 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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

.subtitle {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
  font-style: italic;
}

.footer {
  text-align: center;
  padding: 4rem 0;
  color: #888;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .sources-page {
    padding: 0 15px;
  }

  .header {
    padding: 1.5rem 0;
  }

  .title {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1rem;
    max-width: 90%;
    padding: 0 1rem;
  }
}
</style>