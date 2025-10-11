import json
import google.generativeai as genai
import os
import docx
import fitz  # PyMuPDF for PDF text extraction

os.environ["GOOGLE_API_KEY"] = "AIzaSyAnUzWbWlqs8mGl5Uews4MYGg_uPa7Nknk"
# --------------------------------
# Gemini Setup
# --------------------------------
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set your GOOGLE_API_KEY environment variable.")

genai.configure(api_key=api_key)

model_name = "models/gemini-2.5-pro"
model = genai.GenerativeModel(model_name)

# --------------------------------
# Document Text Extraction Helpers
# --------------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text_from_file(file_path):
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.lower().endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        return "Unsupported file type."

# --------------------------------
# Companion Feedback Function
# --------------------------------
def companion_feedback(question, student_answer, correct_answer=None, max_score=5):
    """
    Returns human-readable feedback, keywords, and improvement steps.
    """
    prompt = f"""
You are a friendly and educational study companion.
Provide guidance in plain English based on the student's answer.

Question: {question}
Student Answer: {student_answer}
Correct Answer: {correct_answer or 'N/A'}
Max Score: {max_score}

Give the response in this format:

Summary: ...
Keywords: ...
Improvement Steps: ...
"""

    response = model.generate_content(prompt).text

    # Parse the model output into sections
    feedback, keywords, steps = "", [], []
    current = None

    for line in response.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("feedback:"):
            current = "feedback"
            feedback = line[len("feedback:"):].strip()
        elif line.lower().startswith("keywords:"):
            current = "keywords"
            keywords = [k.strip() for k in line[len("keywords:"):].split(",") if k.strip()]
        elif line.lower().startswith("improvement steps:"):
            current = "steps"
            steps = [s.strip() for s in line[len("improvement steps:"):].split(";") if s.strip()]
        else:
            if current == "feedback":
                feedback += " " + line
            elif current == "keywords":
                keywords += [k.strip() for k in line.split(",") if k.strip()]
            elif current == "steps":
                steps += [s.strip() for s in line.split(";") if s.strip()]

    return {
        "feedback": feedback or "No feedback available",
        "keywords": keywords,
        "improvement_steps": steps
    }

# --------------------------------
# Test Mode
# --------------------------------
if __name__ == "__main__":
    print("🧠 Gemini Companion Test")
    question = input("Enter your question: ")
    student_answer = input("Enter student's answer: ")
    correct_answer = input("Enter correct answer (optional): ") or None
    max_score = int(input("Enter max score (default 5): ") or 5)

    reply = companion_feedback(question, student_answer, correct_answer, max_score)
    print("\n📢 Summary:\n", reply["feedback"])
    print("\n🔑 Keywords:\n", ", ".join(reply["keywords"]))
    print("\n🚀 Steps to Improve:\n", "\n".join(f"- {s}" for s in reply["improvement_steps"]))
    doc_text = None
    
    reply = companion_feedback(user_input, doc_text)
    print("\n🤖 Companion says:\n", reply)
