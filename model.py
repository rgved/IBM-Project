
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
def companion_feedback(question, student_answer, correct_answer="", max_score=5, document_text=None):
    """
    question: str
    student_answer: str
    correct_answer: str (optional)
    max_score: int (optional)
    document_text: str (optional), content from uploaded file
    """
    context = ""
    if document_text:
        context = f"\nThe user has also provided a document with this content:\n{document_text[:4000]}\n\n"

    prompt = f"""
You are a friendly and knowledgeable study companion.
Your goal is to help the user understand and improve their knowledge through conversation.

Guidelines:
- Explain clearly and politely.
- If the user's message refers to a document, use the document context to give accurate help.
- If you don't know, admit it but guide them where to look.
- Keep responses short, warm, and easy to understand.
- Review the student's answer: "{student_answer}".
- If a correct answer is provided, compare and suggest improvements.
- Provide a score out of {max_score}.
- Also give 3-5 keywords the student should know.
- Give 3 steps to improve the answer.
- Structure your output in JSON like this:
  {{
    "feedback": "...",
    "keywords": ["...", "..."],
    "improvement_steps": ["...", "..."]
  }}

Question: {question}
{context}
"""
    response = model.generate_content(prompt)
    
    # Try parsing JSON from response
    import json
    try:
        return json.loads(response.text.strip())
    except Exception:
        # fallback if parsing fails
        return {
            "feedback": response.text.strip(),
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
