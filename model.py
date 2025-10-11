import json
import google.generativeai as genai
import os
import docx
import fitz  # PyMuPDF for PDF text extraction

# -------------------------------
# Gemini Setup
# -------------------------------
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
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
def companion_feedback(question, student_answer, correct_answer=None, max_score=5):
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

    feedback, keywords, steps = "", [], []
    current = None

    for line in reply_text.splitlines():
        line = line.strip().replace("**", "").lower()
        if not line:
            continue
        if line.startswith("feedback:"):
            current = "feedback"
            feedback = line.split("feedback:")[-1].strip()
        elif line.startswith("keywords:"):
            current = "keywords"
            keywords = [k.strip() for k in line.split("keywords:")[-1].split(",") if k.strip()]
        elif line.startswith("improvement steps:"):
            current = "steps"
            steps = [s.strip() for s in line.split("improvement steps:")[-1].split(";") if s.strip()]
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

# -------------------------------
# Summariser
# -------------------------------
def summarise_text(text):
    prompt = f"Summarize this in clear, concise points:\n\n{text}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, "text") else "⚠️ No summary generated."
    except Exception as e:
        return f"⚠️ Error generating summary: {e}"

# -------------------------------
# Test Run
# -------------------------------
if __name__ == "__main__":
    print("🧠 Gemini Companion Test")
    question = input("Enter your question: ")
    student_answer = input("Enter student's answer: ")
    correct_answer = input("Enter correct answer (optional): ") or None

    result = companion_feedback(question, student_answer, correct_answer)
    print("\n📢 Feedback:", result["feedback"])
    print("\n🔑 Keywords:", ", ".join(result["keywords"]))
    print("\n🚀 Steps to Improve:")
    for s in result["improvement_steps"]:
        print("-", s)
