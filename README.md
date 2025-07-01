# John A. Macdonald History Bot

An AI-powered chatbot that answers questions about Canada's first Prime Minister using historical documents and speeches.

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/ianvanharten/macdonald_history_bot.git
   cd macdonald_history_bot
   ```

2. **Set up Python virtual environment**
   ```bash
   cd api
   python -m venv venv
   venv/Scripts/activate  # On Windows
   pip install -r requirements.txt
   ```

3. **Install Ollama and required models**
   ```bash
   ollama pull gemma2:2b
   ```

4. **Build the vector database**
   ```bash
   python setup_chroma.py
   ```
   This will process all historical documents and create the ChromaDB vector store (~260MB).

5. **Run the API**
   ```bash
   uvicorn main:app --reload
   ```

## Note
The ChromaDB vector store (`chroma_store/`) is excluded from the repository due to its size (260MB). It will be automatically created when you run the setup script.