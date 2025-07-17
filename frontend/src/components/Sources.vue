<template>
  <div class="sources-page">
    <header class="header">
      <h1 class="title">Historical Sources</h1>
      <p class="subtitle">
        Sir John A. MacDonald's responses are grounded in authentic historical documents and speeches from the 19th century.
        This page provides details about the primary sources used to create his knowledge base.
      </p>
    </header>

    <main class="content">
      <div class="sources-list">
        <div class="source-item">
          <h2 class="source-title">House of Commons Debate Transcripts (1867 - 1891)</h2>
          <p class="source-description">
            This is the principle resource for the app. Everything John A. MacDonald ever said in parliament is available in the transcripts for the debates in the House of Commons. All the debates from the Canadian House of Commons going back to the first parliament in 1867 are transcribed and available as pdfs. I scraped them all pulling only the speeches given by John A. MacDonald.
          </p>
          <div class="source-links">
            <a href="https://parl.canadiana.ca/browse" target="_blank" rel="noopener noreferrer" class="source-link">
              Parliament of Canada Historical Debates
            </a>
          </div>
        </div>

        <div class="source-item">
          <h2 class="source-title">Correspondence of Sir John A. MacDonald, edited by Sir Joseph Pope (1921)</h2>
          <p class="source-description">
            A collection of his letters compiled by his literary executor and available online as a pdf.
          </p>
          <div class="source-links">
            <a href="https://primarydocuments.ca/wp-content/uploads/2019/03/PopeMacdonaldCorrespondence.pdf" target="_blank" rel="noopener noreferrer" class="source-link">
              MacDonald Correspondence PDF
            </a>
          </div>
        </div>

        <div class="source-item">
          <h2 class="source-title">The Canadian Encyclopedia</h2>
          <p class="source-description">
            The Canadian Encyclopedia's principle article on Sir John A. MacDonald.
          </p>
          <div class="source-links">
            <a href="https://www.thecanadianencyclopedia.ca/en/article/sir-john-alexander-macdonald" target="_blank" rel="noopener noreferrer" class="source-link">
              Sir John Alexander MacDonald
            </a>
          </div>
        </div>

        <div class="source-item">
          <h2 class="source-title">The Dictionary of Canadian Biography</h2>
          <p class="source-description">
            I used a few resources from here. They have a full biography of John A. MacDonald plus a series of thematic articles looking at his life from the perspective of those themes. Finally, they have a section on Canadian Confederation which I used as well.
          </p>
          <div class="source-links">
            <a href="https://www.biographi.ca/en/bio/macdonald_john_alexander_12E.html" target="_blank" rel="noopener noreferrer" class="source-link">
              John A. MacDonald Biography
            </a>
            <a href="https://www.biographi.ca/en/theme_macdonald.html?p=1" target="_blank" rel="noopener noreferrer" class="source-link">
              MacDonald Thematic Articles
            </a>
            <a href="https://www.biographi.ca/en/theme_confederation.html" target="_blank" rel="noopener noreferrer" class="source-link">
              Canadian Confederation
            </a>
          </div>
        </div>

        <div class="source-item">
          <h2 class="source-title">John A. MacDonald: The Indispensable Politician by Alastair Gillespie</h2>
          <p class="source-description">
            A paper published for the MacDonald Laurier Institute and available online as a pdf.
          </p>
          <div class="source-links">
            <a href="https://macdonaldlaurier.ca/files/pdf/MLIConfederationSeries_MacdonaldPaperF_Web.pdf" target="_blank" rel="noopener noreferrer" class="source-link">
              The Indispensable Politician PDF
            </a>
          </div>
        </div>

        <div class="source-item">
          <h2 class="source-title">Anecdotal Life of Sir John A. MacDonald by Emerson Bristol Biggar (1891)</h2>
          <p class="source-description">
            An old book on a fairly old-looking website, but available in full online.
          </p>
          <div class="source-links">
            <a href="https://www.johnamacdonald.org/" target="_blank" rel="noopener noreferrer" class="source-link">
              Anecdotal Life of Sir John A. MacDonald
            </a>
          </div>
        </div>

        <div class="source-item">
          <h2 class="source-title">Wikipedia</h2>
          <p class="source-description">
            Can't forget wikipedia.
          </p>
          <div class="source-links">
            <a href="https://en.wikipedia.org/wiki/John_A._Macdonald" target="_blank" rel="noopener noreferrer" class="source-link">
              John A. Macdonald - Wikipedia
            </a>
          </div>
        </div>
      </div>
    </main>

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
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
  font-style: italic;
}

.content {
  flex: 1;
  padding: 2rem 0;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.source-item {
  padding: 2rem;
  border-radius: 8px;
}

.source-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1rem;
  line-height: 1.3;
}

.source-description {
  font-size: 1rem;
  color: #444;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.source-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.source-link {
  display: inline-block;
  color: #2563EB;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  border-bottom: 1px solid transparent;
  transition: all 0.3s ease;
}

.source-link:hover {
  color: #1D4ED8;
  border-bottom-color: #2563EB;
}

.source-link:after {
  content: ' ↗';
  font-size: 0.9em;
  opacity: 0.6;
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

  .content {
    padding: 1.5rem 0;
  }

  .sources-list {
    gap: 2rem;
  }

  .source-item {
    padding: 1.5rem;
  }

  .source-title {
    font-size: 1.3rem;
  }

  .source-description {
    font-size: 0.95rem;
  }

  .source-links {
    gap: 0.3rem;
  }
}
</style>