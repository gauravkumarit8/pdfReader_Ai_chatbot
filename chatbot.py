# import requests

# def get_answer(context, question):
#     prompt = f"""Use the following context to answer the user's question.

# Context:
# {context}

# Question:
# {question}

# Answer:"""

#     response = requests.post("http://localhost:11434/api/generate", json={
#         "model": "mistral",
#         "prompt": prompt,
#         "stream": False
#     })

#     return response.json()["response"]


import requests

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def get_answer(context, question):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    prompt = f"""Use the following context to answer the user's question.

Context:
{context}

Question:
{question}

Answer:"""

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def generate_questions(context, num_questions=5):
    prompt = f"""Based on the following context, generate {num_questions} questions a user might ask:

Context:
{context}

Questions:"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return [q.strip("- ").strip() for q in text.strip().split("\n") if q.strip()]
