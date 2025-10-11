import json
import google.generativeai as genai
import os
import docx
import fitz  # PyMuPDF for PDF text extraction

os.environ["GOOGLE_API_KEY"] = "AIzaSyAnUzWbWlqs8mGl5Uews4MYGg_uPa7Nknk"
# --------------------------------
# Gemini Setup
# --------------------------------
# Make sure you set your API key as an environment variable first:
# export GOOGLE_API_KEY="YOUR_API_KEY"
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set your GOOGLE_API_KEY environment variable.")

genai.configure(api_key=api_key)

# Use a stable Gemini model
model_name = "models/gemini-2.5-pro"
model = genai.GenerativeModel(model_name)

# --------------------------------
# Document Text Extraction Helpers
# --------------------------------
def extract_text_from_pdf(file_path):
    """Extract text content from a PDF."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path):
    """Read text from a plain TXT file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text_from_file(file_path):
    """Auto-detect file type and extract text accordingly."""
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
    Returns human-readable feedback text, keywords, and improvement steps as strings/lists.
    """
    user_input = f"Question: {question}\nStudent Answer: {student_answer}\nCorrect Answer: {correct_answer}\nMax Score: {max_score}"

    prompt = f"""
You are a friendly study companion.
Provide guidance in plain English:
- Feedback: tell the student how they did.
- Keywords: give a few key points they should include.
- Improvement Steps: suggest steps to improve their answer.

Format your response like this (but in natural English, not JSON):

Feedback: ...
Keywords: ...
Improvement Steps: ...
"""

    response = model.generate_content(prompt).text

    # Parse response into separate sections
    feedback, keywords, steps = "", [], []

    # Extract sections using simple string parsing
    lines = response.splitlines()
    current = None
    for line in lines:
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
        "feedback": feedback,
        "keywords": keywords,
        "improvement_steps": steps
    }
# --------------------------------
# Test Mode
# --------------------------------
if __name__ == "__main__":
    print("🧠 Gemini Companion Test")
    user_input = input("Type your message: ")
    
    # Optional: test with a document
    # doc_text = extract_text_from_file("example.pdf")
    doc_text = None
    
    reply = companion_feedback(user_input, doc_text)
    print("\n🤖 Companion says:\n", reply)
