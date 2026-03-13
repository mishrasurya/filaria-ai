import streamlit as st
import fitz
import numpy as np
import requests
import os
import re
import time

# =====================================================
# Page Config
# =====================================================
st.set_page_config(
    page_title="Filariasis Knowledge Assistant",
    page_icon="🦟",
    layout="wide"
)

# =====================================================
# Session State
# =====================================================
if "question" not in st.session_state:
    st.session_state.question = ""

if "answer" not in st.session_state:
    st.session_state.answer = None

if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False

# =====================================================
# PROFESSIONAL UI CSS
# =====================================================
st.markdown("""
<style>

.block-container{
max-width:950px;
padding-top:2rem;
}

.hero{
background:linear-gradient(135deg,#3b4261,#4a537a);
padding:40px;
border-radius:16px;
text-align:center;
margin-bottom:40px;
box-shadow:0 10px 25px rgba(0,0,0,0.15);
}

.hero-title{
font-size:42px;
font-weight:700;
color:white;
margin-bottom:8px;
}

.hero-sub{
color:#e6e9ff;
font-size:16px;
}

.stTextInput > div > div > input{
border-radius:16px;
padding:18px 20px;
font-size:18px;
border:1px solid #e4e8ff;
background:white;
box-shadow:0 6px 14px rgba(0,0,0,0.08);
transition:all 0.25s ease;
}

.stTextInput input::placeholder{
color:#9aa0b8;
font-size:17px;
}

.stTextInput > div > div > input:focus{
border:1px solid #5b63ff;
box-shadow:0 0 0 4px rgba(91,99,255,0.15);
outline:none;
}

.stButton button{
background:#3b4261;
color:white;
border-radius:12px;
padding:12px 26px;
font-weight:600;
font-size:16px;
border:none;
box-shadow:0 3px 8px rgba(0,0,0,0.15);
}

.stButton button:hover{
background:#2f3551;
}

.answer-card{
background:white;
padding:32px;
border-radius:16px;
border:1px solid #e6e9ff;
box-shadow:0 8px 18px rgba(0,0,0,0.08);
font-size:17px;
line-height:1.7;
}

.answer-card table{
border-collapse:collapse;
width:100%;
margin-top:10px;
}

.answer-card th{
background:#f2f4ff;
padding:10px;
text-align:left;
}

.answer-card td{
padding:10px;
border-top:1px solid #eee;
}

.source-box{
margin-top:18px;
padding:12px;
background:#eef1ff;
border-radius:10px;
font-size:14px;
text-align:center;
color:#333;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# API Key
# =====================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY not configured.")
    st.stop()

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

# =====================================================
# HERO HEADER
# =====================================================
st.markdown("""
<div class="hero">
<div class="hero-title">🦟 Filariasis Knowledge Assistant</div>
<div class="hero-sub">
Ask any question about filariasis and get answers from
official Government of India health guidelines.
</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# Helper Functions
# =====================================================
def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return " ".join(page.get_text() for page in doc)

def clean_text(text):
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if len(chunk) > 100:
            chunks.append(chunk)
        start = end - overlap
    return chunks

def embed_text(text, retry=True):

    if not text or len(text.strip()) < 10:
        return None

    text = text[:1500]

    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers=HEADERS,
            json=payload,
            timeout=30
        )

        if res.status_code != 200:
            if retry:
                time.sleep(1)
                return embed_text(text, retry=False)
            return None

        data = res.json()

        return np.array(
            data["data"][0]["embedding"],
            dtype="float32"
        )

    except Exception:
        return None


def cosine_similarity(a, b):
    return float(
        np.dot(a, b) /
        (np.linalg.norm(a) * np.linalg.norm(b))
    )


def ask_llm(context, question):

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "user",
                "content": f"""
You are a medical assistant.

Answer clearly using ONLY the context below.

Context:
{context}

Question:
{question}
"""
            }
        ],
        "temperature": 0.2
    }

    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    return res.json()["choices"][0]["message"]["content"]

# =====================================================
# Load Knowledge Base
# =====================================================
@st.cache_resource(show_spinner="Loading knowledge base...")
def load_knowledge_base(pdf_folder):

    documents = []
    embeddings = []

    for filename in os.listdir(pdf_folder):

        if filename.endswith(".pdf"):

            path = os.path.join(pdf_folder, filename)

            raw = extract_text_from_pdf(path)
            cleaned = clean_text(raw)

            chunks = chunk_text(cleaned)[:10]

            for chunk in chunks:

                vec = embed_text(chunk)

                if vec is not None:
                    documents.append(chunk)
                    embeddings.append(vec)

    return documents, embeddings


PDF_FOLDER = "data"

documents, embeddings = load_knowledge_base(PDF_FOLDER)

# =====================================================
# Suggested Questions
# =====================================================
st.markdown("### Suggested Questions")

col1, col2, col3, col4 = st.columns(4)

examples = [
    "What is lymphatic filariasis?",
    "How does filariasis spread?",
    "Symptoms of filariasis?",
    "Mass Drug Administration?"
]

selected_question = None

for i, example in enumerate(examples):

    if [col1, col2, col3, col4][i].button(example):
        selected_question = example

if selected_question:
    st.session_state.question = selected_question

# =====================================================
# Search Input
# =====================================================
def trigger_search():
    st.session_state.search_triggered = True

question = st.text_input(
    "",
    key="question",
    placeholder="Ask something about Filariasis...",
    on_change=trigger_search
)

search_clicked = st.button("Search")

SIMILARITY_THRESHOLD = 0.25

# =====================================================
# Search
# =====================================================
if search_clicked or st.session_state.search_triggered:

    st.session_state.search_triggered = False

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    q_vec = embed_text(question)

    scores = []

    for doc, vec in zip(documents, embeddings):

        score = cosine_similarity(q_vec, vec)

        if score > SIMILARITY_THRESHOLD:
            scores.append((score, doc))

    if not scores:
        st.session_state.answer = None

        st.warning(
            "I couldn't find information about that in the filariasis guidelines. "
            "Please try asking a question related to filariasis."
        )

        st.stop()

    scores.sort(reverse=True)

    top_chunks = scores[:3]

    context = "\n\n".join(c[1] for c in top_chunks)

    with st.spinner("Generating answer..."):

        answer = ask_llm(context, question)

    st.session_state.answer = answer

# =====================================================
# Answer
# =====================================================
if st.session_state.answer:

    st.markdown("### Answer")

    clean_answer = st.session_state.answer.replace("<br>", "\n")

    st.markdown(
        f"""
<div class="answer-card">

{clean_answer}

</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="source-box">
Answer generated from Government of India
Filariasis Elimination Guidelines (2018 & 2024)
</div>
""",
        unsafe_allow_html=True
    )