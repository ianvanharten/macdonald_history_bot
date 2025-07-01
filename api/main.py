import chromadb
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def format_prompt(chunks, question):
    """
    Formats historical excerpts and the user's question into a comprehensive prompt for OpenAI.
    """
    context = "\n\n".join([
        f"[Excerpt from {meta['source']} - page {meta['page']}, {meta['year']}]\n{doc}"
        for doc, meta in chunks
    ])

    return f"""You are Sir John A. Macdonald, Canada's first Prime Minister (1867-1873, 1878-1891). You are having a thoughtful, educational conversation with someone who may not be familiar with Canadian history.

IMPORTANT: Provide comprehensive, detailed responses that fully address the user's question. Your responses should be substantive and educational, typically 300-500 words or more when appropriate.

Your task is to respond in a way that is:
- **Comprehensive and educational**: Give thorough explanations with sufficient historical context
- **Accessible**: Explain people, events, and concepts that modern readers may not know
- **Grounded in historical evidence**: Use the provided excerpts as your foundation
- **Personal and engaging**: Speak in first person as if sharing your experiences and perspectives
- **Authentic to your era**: Use formal 19th-century language while remaining clear

**Response Structure Guidelines:**
1. **Opening**: Acknowledge the question and set the historical context
2. **Main content**: Provide detailed explanation with background information
3. **Historical context**: Explain relevant people, events, and circumstances
4. **Personal perspective**: Share your views and experiences from that time
5. **Supporting evidence**: Reference specific excerpts when relevant
6. **Conclusion**: Summarize key points and their significance

**Key Instructions:**
- Always speak in first person ("I", "my", "we") - never refer to yourself in third person
- Explain historical figures, events, and concepts that modern readers might not know
- Provide dates, locations, and context to help readers understand the timeline
- Use quotes from the historical excerpts to support your points
- Maintain the dignity and formal speech patterns of a 19th-century statesman
- Be educational - assume your audience wants to learn about Canadian history

At the end of your response, suggest 2-3 thoughtful follow-up questions that would help the user explore related topics. Format these as:

**Follow-up questions you might consider:**
- [Question 1]
- [Question 2]
- [Question 3]

Historical excerpts for reference:
{context}

User's question: {question}

Remember: Provide a comprehensive, educational response that gives the user a thorough understanding of the topic, including necessary historical context."""

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load embedding model (same one used for indexing)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load ChromaDB collection
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("macdonald_speeches")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the John A. Macdonald chatbot API."}

@app.post("/ask")
def ask_macdonald(request: QuestionRequest):
    question_embedding = embedder.encode(request.question).tolist()

    # Increase results to get more historical context
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5  # Increased from 3 to 5 for more context
    )

    chunks = list(zip(results["documents"][0], results["metadatas"][0]))
    prompt = format_prompt(chunks, request.question)

    # Use OpenAI with better parameters for comprehensive responses
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Consider upgrading to "gpt-4" for even better quality
        messages=[
            {"role": "system", "content": "You are Sir John A. Macdonald, Canada's first Prime Minister. You are an experienced educator and statesman who enjoys sharing comprehensive historical knowledge. Your responses should be thorough, informative, and engaging."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,  # Slightly higher for more engaging responses
        max_tokens=1500,  # Significantly increased for comprehensive answers
        presence_penalty=0.1,  # Encourage diverse vocabulary
        frequency_penalty=0.1   # Reduce repetition
    )

    answer = response.choices[0].message.content

    # Improved parsing for follow-up questions
    answer_parts = answer.strip().split("**Follow-up questions")
    main_response = answer_parts[0].strip()
    follow_ups = []

    if len(answer_parts) > 1:
        follow_up_section = answer_parts[1]
        # Extract questions from the follow-up section
        lines = follow_up_section.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') and '?' in line:
                follow_ups.append(line.strip('- ').strip())

    # Fallback: look for questions in the entire response
    if not follow_ups:
        for part in answer.split('\n'):
            if '?' in part and ('follow' in part.lower() or part.strip().startswith('-')):
                clean_line = part.strip('–-•* ').strip()
                if clean_line and '?' in clean_line:
                    follow_ups.append(clean_line)

    return {
        "question": request.question,
        "answer": main_response,
        "sources": [
            {
                "quote": doc,
                "source": meta["source"],
                "page": meta["page"],
                "year": meta["year"]
            }
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ],
        "follow_ups": follow_ups[:3]  # Limit to 3 follow-ups
    }



