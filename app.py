from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import json 
from pdf_loader import extract_text_from_pdf
from vector_store import VectorStore
from chatbot import get_answer, generate_questions
from feedback_logger import log_feedback

app = FastAPI()
vector_store = VectorStore()

suggested_questions_store = []

# ✅ Move this here (above the route)
class Feedback(BaseModel):
    question: str
    context: str
    answer: str
    feedback: str  # 'up' or 'down'

class Query(BaseModel):
    question: str

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    global suggested_questions_store

    file_path = "product_manual.pdf"

    try:
        # ✅ Save the uploaded file
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        with open(file_path, "wb") as f:
            f.write(contents)

        # ✅ Check if file is saved and has size
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise HTTPException(status_code=400, detail="Saved file is empty or corrupted.")

        # ✅ Extract and vectorize
        text = extract_text_from_pdf(file_path)
        vector_store.add_texts(text, metadata_base={"source": file.filename})

        # ✅ Generate suggested questions
        try:
            suggested_questions = generate_questions(text, num_questions=7)
            suggested_questions_store = suggested_questions
        except Exception as e:
            suggested_questions = ["Could not generate questions."]
            suggested_questions_store = suggested_questions

        return {
            "message": "PDF processed and loaded into memory.",
            "suggested_questions": suggested_questions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")


# @app.post("/upload_pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
    # global suggested_questions_store

    # contents = await file.read()
    # with open("product_manual.pdf", "wb") as f:
    #     f.write(contents)

    # text = extract_text_from_pdf("product_manual.pdf")
    # # chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
    # # vector_store.add_texts(chunks)
    # vector_store.add_texts(text, metadata_base={"source": file.filename})

    # try:
    #     suggested_questions = generate_questions(text, num_questions=7)
    #     suggested_questions_store = suggested_questions
    # except Exception as e:
    #     suggested_questions = ["Could not generate questions."]
    #     suggested_questions_store = suggested_questions

    # return {
    #     "message": "PDF processed and loaded into memory.",
    #     "suggested_questions": suggested_questions
    # }

@app.post("/ask/")
async def ask_question(query: Query):
    try:
        top_chunks = vector_store.search(query.question)
        context = "\n".join([chunk["text"] for chunk in top_chunks])
        answer = get_answer(context, query.question)
        return {"answer": answer}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})



@app.get("/suggested_questions/")
async def get_suggested_questions():
    if not suggested_questions_store:
        return {"message": "No suggested questions found. Upload a PDF first."}
    return {"suggested_questions": suggested_questions_store}




@app.get("/use_first_suggested/")
async def use_first_suggested_question():
    if suggested_questions_store:
        question = None
        for q in suggested_questions_store:
            if not q.lower().startswith("here are") and q.strip().endswith("?"):
                question = q
                break
        
        if not question:
            question = suggested_questions_store[0]

        top_chunks = vector_store.search(question)
        context = "\n".join([chunk["text"] for chunk in top_chunks])
        answer = get_answer(context, question)
        return {
            "used_prompt": question,
            "answer": answer
        }
    return {"message": "No suggested questions found."}




@app.post("/feedback/")
async def give_feedback(feedback: Feedback):
    log_feedback(
        question=feedback.question,
        context=feedback.context,
        answer=feedback.answer,
        feedback=feedback.feedback
    )
    return {"message": "Feedback received."}



@app.get("/feedbacks/")
async def get_all_feedback():
    try:
        with open("feedback.json", "r") as f:
            feedback_data = json.load(f)
        return {"feedback": feedback_data}
    except FileNotFoundError:
        return {"feedback": []}
