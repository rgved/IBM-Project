
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
def companion_feedback(user_input, student_answer=None, correct_answer=None, max_score=5):
    """
    AI companion mode: friendly, educational guidance.
    Returns a dictionary with keys: feedback, keywords, improvement_steps.
    """
    context = ""
    if student_answer:
        context += f"\nStudent Answer: {student_answer}"
    if correct_answer:
        context += f"\nCorrect Answer: {correct_answer}"

    prompt = f"""
You are a friendly and knowledgeable study companion.
Provide guidance in JSON format with keys:
- feedback: concise feedback on the student's answer
- keywords: list of important keywords for a perfect answer
- improvement_steps: actionable steps to improve

User Question: {user_input}
{context}
Max Score: {max_score}

Respond ONLY in JSON format.
"""

    response = model.generate_content(prompt).text.strip()

    # Ensure we return a dictionary
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # fallback if the model didn't return proper JSON
        return {
            "feedback": response,
            "keywords": [],
            "improvement_steps": []
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
