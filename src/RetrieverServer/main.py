from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging

from src.RetrieverServer.retriever import embedding_question, similarity_search
from src.RetrieverServer.model_prompting import send_prompt_to_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(
    title="Personal Knowledge Assistant API",
    description="API for document retrieval and question answering",
    version="1.0.0"
)

# Load environment variables
EMBEDDING_MODEL_URL = os.getenv("EMBEDDING_MODEL_URL")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")

# Log configuration on startup
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Personal Knowledge Assistant API - Configuration")
    logger.info("=" * 60)
    logger.info(f"EMBEDDING_MODEL_URL: {EMBEDDING_MODEL_URL}")
    logger.info(f"WEAVIATE_URL: {WEAVIATE_URL}")
    logger.info(f"OLLAMA_URL: {OLLAMA_URL}")
    logger.info("=" * 60)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/search",
          summary="Search for answers",
          description="Submit a question and get an answer from the knowledge base")
async def get_answer(request: QuestionRequest):
    logger.info(f"Received question: {request.question}")

    try:
        logger.info("Step 1: Getting embedding...")
        embedded_question = embedding_question(request.question, EMBEDDING_MODEL_URL)
        logger.info(f"Embedding received: {len(embedded_question)} dimensions")

        logger.info("Step 2: Searching in Weaviate...")
        db_data = similarity_search(WEAVIATE_URL, embedded_question)
        logger.info(f"Found {len(db_data)} results from database")

        template = """Use the following pieces of context to answer the question at the end.
      If you don't know the answer, just say that you don't know, don't try to make up an answer.
      Use three sentences maximum and keep the answer as concise as possible.
      Always say "thanks for asking!" at the end of the answer.

      {db_data}

      Question: {question}

      Helpful Answer:"""

        # Fill in the template
        formatted_prompt = template.format(
            db_data=db_data,
            question=request.question
        )

        logger.info("Step 3: Sending to LLM...")
        answer = send_prompt_to_model(formatted_prompt)
        logger.info("LLM response received")

        return {"question": request.question, "answer": answer}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise