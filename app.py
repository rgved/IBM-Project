import streamlit as st
import json
import docx
import fitz  # PyMuPDF for PDF text extraction
from io import BytesIO
from model import companion_feedback  # updated model.py function
import re

st.set_page_config(page_title="AI Companion Tutor", layout="wide")

# ---------------------------
# File Parsing Helpers
# ---------------------------
def pdf_to_text(file):
    try:
        pdf_data = file.read()
        pdf_file = BytesIO(pdf_data)
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"❌ PDF extraction failed: {e}")
        return ""

def docx_to_text(file):
    try:
        doc_obj = docx.Document(file)
        return "\n".join([p.text for p in doc_obj.paragraphs if p.text.strip()]).strip()
    except Exception as e:
        st.error(f"❌ DOCX extraction failed: {e}")
        return ""

def detect_question(line):
    keywords = [
        r'\bdefine\b', r'\bdescribe\b', r'\bshow\b', r'\billustrate\b',
        r'\belaborate\b', r'\bexplain\b', r'\bgive\b',
        r'\bwho\b', r'\bwhat\b', r'\bwhere\b', r'\bwhen\b', r'\bwhy\b', r'\bhow\b'
    ]
    pattern = r'(\?$|:\s*$|' + "|".join(keywords) + r')'
    return re.search(pattern, line.strip(), flags=re.IGNORECASE)

def smart_parse_text_to_json(raw_text):
    raw_text = re.sub(r'\n+', '\n', raw_text.strip())
    lines = raw_text.split("\n")
    questions, current_q, current_a = [], None, []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if detect_question(line) or re.match(r'^\d+[\).]', line):
            if current_q:
                questions.append({
                    "question_id": f"Q{len(questions)+1}",
                    "question": current_q,
                    "student_answer": " ".join(current_a).strip(),
                    "correct_answer": ""
                })
            current_q, current_a = line, []
        else:
            current_a.append(line)
    if current_q:
        questions.append({
            "question_id": f"Q{len(questions)+1}",
            "question": current_q,
            "student_answer": " ".join(current_a).strip(),
            "correct_answer": ""
        })
    return questions

# ---------------------------
# Companion Mode UI
# ---------------------------
st.title("🤝 AI Companion Tutor")
st.write("Get guided feedback on your answers and learn how to improve!")

upload_option = st.radio("Choose Input Method", ["✏️ Manual Input", "📂 Upload File"])

question = ""
student_answer = ""
correct_answer = ""

# --- Manual Input ---
if upload_option == "✏️ Manual Input":
    question = st.text_area("Enter your Question")
    student_answer = st.text_area("Enter your Answer")
    correct_answer = st.text_area("Correct Answer (optional, for better guidance)")

# --- File Upload ---
elif upload_option == "📂 Upload File":
    file = st.file_uploader("Upload a JSON, PDF, or DOCX file", type=["json", "pdf", "docx"])
    if file:
        st.success(f"✅ Uploaded: {file.name}")
        if file.name.endswith(".pdf"):
            raw_text = pdf_to_text(file)
            parsed = smart_parse_text_to_json(raw_text)
        elif file.name.endswith(".docx"):
            raw_text = docx_to_text(file)
            parsed = smart_parse_text_to_json(raw_text)
        elif file.name.endswith(".json"):
            parsed = json.load(file)
        else:
            parsed = []

        if parsed:
            q_idx = st.number_input("Select Question Index", min_value=1, max_value=len(parsed), value=1)
            selected = parsed[q_idx - 1]
            question = selected.get("question", "")
            student_answer = selected.get("student_answer", "")
            correct_answer = selected.get("correct_answer", "")

            st.write(f"**Question:** {question}")
            st.write(f"**Student Answer:** {student_answer}")

max_score = st.number_input("Max Score", min_value=1, max_value=10, value=5)

# --- Generate Feedback ---
if st.button("Get Guidance"):
    if not question or not student_answer:
        st.warning("Please provide a question and your answer.")
    else:
        with st.spinner("Generating feedback..."):
            # Call the updated companion_feedback
            result = companion_feedback(question, student_answer, correct_answer, max_score)

        # Display Feedback
        st.subheader("📢 Feedback")
        st.write(result.get("feedback", "No feedback available"))

        # Display Keywords
        st.subheader("🔑 Keywords for a Perfect Answer")
        keywords = result.get("keywords", [])
        st.write(", ".join(keywords) if keywords else "No keywords found")

        # Display Improvement Steps
        st.subheader("🚀 Steps to Improve")
        steps = result.get("improvement_steps", [])
        if steps:
            for step in steps:
                st.markdown(f"- {step}")
        else:
            st.write("No improvement steps available")
