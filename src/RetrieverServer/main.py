from fastapi import FastAPI
from pydantic import BaseModel
from retriever import embedding_question
from model_prompting import send_prompt_to_model
from dotenv import load_dotenv
import os

from src.RetrieverServer.retriever import similarity_search

load_dotenv()
app = FastAPI(
    title="Personal Knowledge Assistant API",
    description="API for document retrieval and question answering",
    version="1.0.0"
)
load_dotenv()
EMBEDDING_MODEL_URL=os.getenv("EMBEDDING_MODEL_URL")
WEAVIATE_URL=os.getenv("WEAVIATE_URL")

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/search",
         summary="Search for answers",
         description="Submit a question and get an answer from the knowledge base")
async def get_answer(request: QuestionRequest):
    embedded_question = embedding_question(request.question,EMBEDDING_MODEL_URL)
    db_data = similarity_search(WEAVIATE_URL,embedded_question)
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
    answer = send_prompt_to_model(formatted_prompt)
    return {"question": request.question, "answer": answer}