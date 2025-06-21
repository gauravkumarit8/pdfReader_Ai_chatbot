import json
from datetime import datetime

FEEDBACK_FILE = "feedback.json"

def log_feedback(question, context, answer, feedback):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "context": context,
        "answer": answer,
        "feedback": feedback  # either 'up' or 'down'
    }

    # Load existing feedback
    try:
        with open(FEEDBACK_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Append new feedback
    data.append(entry)

    # Save updated feedback list
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)
