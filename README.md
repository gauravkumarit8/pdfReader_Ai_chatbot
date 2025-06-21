# 🤖 AI PDF Reader & ChatBot

This is an AI-powered application that allows users to upload PDF files (such as product manuals, resumes, or reports), automatically generate suggested questions from the content, and ask further questions to get intelligent answers using Google's Gemini API.

---

## 🚀 Features

- 📄 Upload and parse PDF documents.
- 💬 Auto-generate relevant questions based on uploaded content.
- 🧠 Ask custom or suggested questions using Gemini AI (via Google Generative Language API).
- 🔎 Vector search support (can be switched to Google Vertex AI Vector Search).
- 🌐 FastAPI-based backend.
- 🔧 Ready to be deployed (free hosting support below).

---

## 📁 Project Structure

aipdfreader/
├── app.py # FastAPI app with endpoints
├── chatbot.py # Handles Gemini API call
├── pdf_loader.py # Extracts text from PDF
├── vector_store.py # Handles text storage & semantic search
├── question_generator.py # Auto-generates questions
├── README.md # This file
├── requirements.txt # Dependencies


---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/gauravkumarit8/aiChatBot.git
cd aiChatBot
```

## Instruction to run 
```
uvicorn app:app --reload
```
