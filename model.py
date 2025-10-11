import json
import google.generativeai as genai
import os
import docx
import fitz  # PyMuPDF for PDF text extraction

# -------------------------------
# Gemini Setup
# -------------------------------
os.environ["GOOGLE_API_KEY"] = "AIzaSyAnUzWbWlqs8mGl5Uews4MYGg_uPa7Nknk"
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("models/gemini-2.5-pro")

# -------------------------------
# File Helpers
# -------------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

# -------------------------------
# Companion Feedback
# -------------------------------
def companion_feedback(question, student_answer, correct_answer=None, max_score=5, debug=False):
    """
    Returns structured feedback, keywords, and improvement steps.
    """
    prompt = f"""
You are a supportive study companion.
Analyze the student's answer, compare it to the correct answer (if available),
and provide detailed, constructive feedback.

Question: {question}
Student Answer: {student_answer}
Correct Answer: {correct_answer or "N/A"}
Max Score: {max_score}

Respond clearly in this structure:

Feedback: <your feedback here>
Keywords: <comma-separated key terms>
Improvement Steps: <semicolon-separated steps>
"""

    try:
        response = model.generate_content(prompt)
        reply_text = response.text if response and hasattr(response, "text") else ""
    except Exception as e:
        return {"feedback": f"⚠️ Error: {e}", "keywords": [], "improvement_steps": []}

    if debug:
        print("🧩 Raw model response:", reply_text)

    feedback, keywords, steps = "", [], []
    current = None

    for line in reply_text.splitlines():
        line = line.strip()
        if not line:
            continue

        lower_line = line.lower()

        # Detect section headers more flexibly
        if "feedback" in lower_line and ":" in line:
            current = "feedback"
            feedback = line.split(":", 1)[-1].strip()
        elif "keywords" in lower_line and ":" in line:
            current = "keywords"
            keywords = [k.strip() for k in line.split(":", 1)[-1].split(",") if k.strip()]
        elif ("improvement steps" in lower_line or "steps" in lower_line) and ":" in line:
            current = "steps"
            steps = [s.strip() for s in line.split(":", 1)[-1].split(";") if s.strip()]
        else:
            if current == "feedback":
                feedback += " " + line
            elif current == "keywords":
                keywords += [k.strip() for k in line.split(",") if k.strip()]
            elif current == "steps":
                steps += [s.strip() for s in line.split(";") if s.strip()]

    # Fallbacks if model didn't provide sections
    if not feedback:
        feedback = "⚠️ No feedback generated. Try rephrasing your question or answer."
    if not keywords:
        keywords = ["No keywords found"]
    if not steps:
        steps = ["No improvement steps found"]

    return {"feedback": feedback, "keywords": keywords, "improvement_steps": steps}

# -------------------------------
# Summariser
# -------------------------------
def summarise_text(text, debug=False):
    prompt = f"Summarize this in clear, concise points:\n\n{text}"
    try:
        response = model.generate_content(prompt)
        summary = response.text.strip() if response and hasattr(response, "text") else ""
    except Exception as e:
        return f"⚠️ Error generating summary: {e}"

    if debug:
        print("🧩 Raw summary response:", summary)

    if not summary:
        return "⚠️ No summary generated. Try with shorter or simpler text."
    return summary

# -------------------------------
# Test Run
# -------------------------------
if __name__ == "__main__":
    print("🧠 Gemini Companion Test")
    question = input("Enter your question: ")
    student_answer = input("Enter student's answer: ")
    correct_answer = input("Enter correct answer (optional): ") or None

    result = companion_feedback(question, student_answer, correct_answer, debug=True)
    print("\n📢 Feedback:", result["feedback"])
    print("\n🔑 Keywords:", ", ".join(result["keywords"]))
    print("\n🚀 Steps to Improve:")
    for s in result["improvement_steps"]:
        print("-", s)
