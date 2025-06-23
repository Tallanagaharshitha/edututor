from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from quiz_generator import generate_quiz_and_answers

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    num_questions: int

@app.post("/generate-quiz/")
async def generate_quiz(req: QuizRequest):
    questions, answers = generate_quiz_and_answers(req.topic, req.difficulty, req.num_questions)
    return {"questions": questions, "answers": answers}