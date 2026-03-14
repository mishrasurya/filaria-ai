import streamlit as st
import fitz
import numpy as np
import requests
import os
import re
import time
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="FilariaAI",
    page_icon="🦟",
    layout="wide"
)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "embeddings" not in st.session_state:
    st.session_state.embeddings = []

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "message_timestamps" not in st.session_state:
    st.session_state.message_timestamps = []

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.header("About")

    st.write(
        "This assistant answers questions about **Lymphatic Filariasis** using Government of India elimination guidelines."
    )

    st.divider()

    theme = st.radio(
        "Theme",
        ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1
    )

    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

    st.divider()

    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.session_state.message_timestamps = []
        st.rerun()

    st.divider()

    st.subheader("💡 Example Questions")

    examples = [
        "What is lymphatic filariasis?",
        "How does filariasis spread?",
        "Symptoms of filariasis?",
        "What is Mass Drug Administration?",
        "How to prevent filariasis?",
        "Which states are affected in India?",
    ]

# ---------------------------------------------------
# LIGHT THEME
# ---------------------------------------------------

light_css = """
<style>

/* ── Reset Streamlit chrome ── */
html, body, [data-testid="stAppViewContainer"], .main {
    background: #f5f7fb !important;
    color: #111827 !important;
}

/* Top toolbar / header bar */
[data-testid="stHeader"],
header[data-testid="stHeader"] {
    background: #f5f7fb !important;
    border-bottom: 1px solid #e5e7eb !important;
}

/* Bottom input toolbar */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
.stBottom {
    background: #f5f7fb !important;
    border-top: 1px solid #e5e7eb !important;
}

/* Main block container */
[data-testid="stMainBlockContainer"],
.block-container {
    background: #f5f7fb !important;
    padding-top: 1rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb !important;
}

[data-testid="stSidebar"] * {
    color: #1F3FD6 !important;
}

/* Sidebar body text (About paragraph) stays readable dark */
[data-testid="stSidebar"] p {
    color: #374151 !important;
}

/* Bold text inside About */
[data-testid="stSidebar"] strong {
    color: #1F3FD6 !important;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #1F3FD6, #2F5BFF, #5B7CFF);
    padding: 48px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 20px 45px rgba(47,91,255,0.25);
}

.hero-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
}

.hero-subtitle {
    color: #e6ecff;
    font-size: 17px;
    font-weight: 500;
    margin-top: 8px;
    letter-spacing: 0.01em;
}

.hero-sub {
    color: #e6ecff;
    font-size: 16px;
}

/* Welcome card */
.welcome-card {
    background: white;
    border-radius: 18px;
    padding: 36px 40px;
    text-align: center;
    box-shadow: 0 6px 24px rgba(47,91,255,0.10);
    margin: 10px auto 32px auto;
    max-width: 700px;
    border: 1px solid #e0e7ff;
}

.welcome-card h2 {
    color: #1F3FD6;
    font-size: 26px;
    margin-bottom: 10px;
}

.welcome-card p {
    color: #4b5563;
    font-size: 15px;
    line-height: 1.6;
}

.welcome-card .topics {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
}

.topic-chip {
    background: #eef2ff;
    color: #1F3FD6;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    border: 1px solid #c7d2fe;
}

/* Timestamp */
.msg-timestamp {
    font-size: 11px;
    color: #9ca3af;
    text-align: right;
    margin-top: 4px;
    padding-right: 4px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: white !important;
    padding: 16px !important;
    border-radius: 14px !important;
    border-left: 4px solid #2F5BFF !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
    color: #111827 !important;
}

[data-testid="stChatMessage"] * {
    color: #111827 !important;
}

/* Chat input box — premium light */
[data-testid="stChatInputContainer"] {
    background: white !important;
    border-radius: 16px !important;
    border: 2px solid #6b7280 !important;
    box-shadow: 0 4px 24px rgba(47,91,255,0.08), 0 1px 4px rgba(0,0,0,0.08) !important;
    padding: 4px 8px !important;
    transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
}

[data-testid="stChatInputContainer"]:focus-within {
    border-color: #2F5BFF !important;
    box-shadow: 0 0 0 3px rgba(47,91,255,0.15), 0 4px 24px rgba(47,91,255,0.18) !important;
}

[data-testid="stChatInput"],
textarea {
    background: transparent !important;
    color: #111827 !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
    letter-spacing: 0.01em !important;
}

textarea::placeholder {
    color: #9ca3af !important;
    font-style: italic !important;
}

/* Send button glow — light */
[data-testid="stChatInputContainer"] button {
    background: linear-gradient(135deg, #2F5BFF, #1F3FD6) !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(47,91,255,0.35) !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
}

[data-testid="stChatInputContainer"] button:hover {
    box-shadow: 0 4px 16px rgba(47,91,255,0.5) !important;
    transform: scale(1.05) !important;
}

[data-testid="stChatInputContainer"] button svg {
    color: white !important;
    fill: white !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
    background: #2F5BFF !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    margin-bottom: 8px !important;
    white-space: nowrap !important;
    font-size: 13px !important;
    padding: 6px 10px !important;
    width: 100% !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

section[data-testid="stSidebar"] button * {
    color: white !important;
}

section[data-testid="stSidebar"] button:hover {
    background: #1F3FD6 !important;
}

</style>
"""

# ---------------------------------------------------
# DARK THEME
# ---------------------------------------------------

dark_css = """
<style>

/* ── Reset Streamlit chrome ── */
html, body, [data-testid="stAppViewContainer"], .main {
    background: #0f172a !important;
    color: #f1f5f9 !important;
}

/* Top toolbar / header bar — the white strip at top */
[data-testid="stHeader"],
header[data-testid="stHeader"],
[data-testid="stToolbar"],
.stAppHeader {
    background: #0f172a !important;
    border-bottom: 1px solid #1e293b !important;
}

/* Bottom input toolbar */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
.stBottom,
div[class*="stBottom"] {
    background: #0f172a !important;
    border-top: 2px solid #334155 !important;
    padding: 12px 16px !important;
}

/* Main block container */
[data-testid="stMainBlockContainer"],
.block-container {
    background: #0f172a !important;
    padding-top: 1rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617 !important;
    border-right: 1px solid #1e293b !important;
}

[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #020617, #1e3a8a, #2563eb);
    padding: 48px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 20px 45px rgba(0,0,0,0.6);
}

.hero-title {
    font-size: 42px;
    font-weight: 700;
    color: white;
}

.hero-subtitle {
    color: #cbd5f5;
    font-size: 17px;
    font-weight: 500;
    margin-top: 8px;
    letter-spacing: 0.01em;
}

.hero-sub {
    color: #cbd5f5;
    font-size: 16px;
}

/* Welcome card */
.welcome-card {
    background: #1e293b;
    border-radius: 18px;
    padding: 36px 40px;
    text-align: center;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    margin: 10px auto 32px auto;
    max-width: 700px;
    border: 1px solid #334155;
}

.welcome-card h2 {
    color: #93c5fd;
    font-size: 26px;
    margin-bottom: 10px;
}

.welcome-card p {
    color: #94a3b8;
    font-size: 15px;
    line-height: 1.6;
}

.welcome-card .topics {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
}

.topic-chip {
    background: #1e3a8a;
    color: #93c5fd;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    border: 1px solid #2563eb;
}

/* Timestamp */
.msg-timestamp {
    font-size: 11px;
    color: #64748b;
    text-align: right;
    margin-top: 4px;
    padding-right: 4px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    padding: 16px !important;
    border-radius: 14px !important;
    border-left: 4px solid #3b82f6 !important;
    box-shadow: 0 5px 20px rgba(0,0,0,0.5) !important;
}

[data-testid="stChatMessage"] * {
    color: #f1f5f9 !important;
}

/* Chat input — premium dark */
div[data-testid="stChatInputContainer"] {
    background: #1c1f26 !important;
    border-radius: 24px !important;
    border: 2px solid #4a4f5e !important;
    box-shadow: none !important;
    padding: 8px 12px !important;
}

div[data-testid="stChatInputContainer"]:focus-within {
    border: 2px solid #7c8cff !important;
    box-shadow: 0 0 0 3px rgba(124,140,255,0.2) !important;
}

[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
[data-testid="stChatInputContainer"] textarea,
[data-testid="stChatInputContainer"] input {
    background: transparent !important;
    color: #f1f5f9 !important;
    -webkit-text-fill-color: #f1f5f9 !important;
    caret-color: #60a5fa !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
    letter-spacing: 0.01em !important;
}

textarea::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
    font-style: italic !important;
}

/* Send button glow — dark */
[data-testid="stChatInputContainer"] button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 2px 10px rgba(59,130,246,0.4) !important;
    transition: box-shadow 0.2s ease, transform 0.15s ease !important;
}

[data-testid="stChatInputContainer"] button:hover {
    box-shadow: 0 4px 20px rgba(59,130,246,0.6) !important;
    transform: scale(1.05) !important;
}

[data-testid="stChatInputContainer"] button svg {
    color: white !important;
    fill: white !important;
}

/* Spinner / status elements */
[data-testid="stSpinner"] * {
    color: #f1f5f9 !important;
}

/* Markdown text */
.stMarkdown, .stMarkdown * {
    color: #f1f5f9 !important;
}

/* Radio button labels */
[data-testid="stRadio"] label,
[data-testid="stRadio"] span {
    color: #f1f5f9 !important;
}

/* Divider */
hr {
    border-color: #1e293b !important;
}

/* General text fallback */
p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: inherit !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 6px;
    background: #0f172a;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {
    background: #2563eb !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    margin-bottom: 8px !important;
    white-space: nowrap !important;
    font-size: 13px !important;
    padding: 6px 10px !important;
    width: 100% !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

section[data-testid="stSidebar"] button:hover {
    background: #1d4ed8 !important;
}

</style>
"""

if st.session_state.theme == "Light":
    st.markdown(light_css, unsafe_allow_html=True)
else:
    st.markdown(dark_css, unsafe_allow_html=True)

# JS: Force input box styles for dark mode (bypasses Streamlit CSS specificity)
if st.session_state.theme == "Dark":
    st.components.v1.html("""
    <script>
    (function styleInput() {
        function applyStyles() {
            var containers = document.querySelectorAll('[data-testid="stChatInputContainer"]');
            containers.forEach(function(el) {
                el.style.setProperty('background', '#1c1f26', 'important');
                el.style.setProperty('border', '2px solid #4a4f5e', 'important');
                el.style.setProperty('border-radius', '24px', 'important');
                el.style.setProperty('box-shadow', 'none', 'important');
                el.style.setProperty('padding', '8px 12px', 'important');
            });
            var textareas = document.querySelectorAll('[data-testid="stChatInputContainer"] textarea, [data-testid="stChatInputContainer"] input');
            textareas.forEach(function(el) {
                el.style.setProperty('color', '#e2e8f0', 'important');
                el.style.setProperty('-webkit-text-fill-color', '#e2e8f0', 'important');
                el.style.setProperty('caret-color', '#7c8cff', 'important');
                el.style.setProperty('background', 'transparent', 'important');
                el.style.setProperty('font-size', '15px', 'important');
            });
        }
        applyStyles();
        setInterval(applyStyles, 500);
        var observer = new MutationObserver(applyStyles);
        observer.observe(document.body, { childList: true, subtree: true });
    })();
    </script>
    """, height=0, scrolling=False)

# ---------------------------------------------------
# HERO
# ---------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-title">🦟 FilariaAI</div>
    <div class="hero-subtitle">AI Assistant for Lymphatic Filariasis based on Government of India Elimination Guidelines.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# API KEY
# ---------------------------------------------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY not configured.")
    st.stop()

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# ---------------------------------------------------
# CLEAN ANSWER
# ---------------------------------------------------

def clean_answer(text):
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<.*?>", "", text)
    return text.strip()

# ---------------------------------------------------
# PDF PROCESSING
# ---------------------------------------------------

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    return " ".join(page.get_text() for page in doc)

def clean_text(text):
    return re.sub(r"\s+", " ", text)

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

# ---------------------------------------------------
# EMBEDDING
# ---------------------------------------------------

def embed_text(text):
    payload = {
        "model": "text-embedding-3-small",
        "input": text[:1500]
    }
    res = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers=HEADERS,
        json=payload
    )
    data = res.json()
    return np.array(data["data"][0]["embedding"], dtype="float32")

# ---------------------------------------------------
# SIMILARITY
# ---------------------------------------------------

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# ---------------------------------------------------
# LOAD KNOWLEDGE
# ---------------------------------------------------

@st.cache_resource
def _load_knowledge_cached(pdf_folder):   # renamed with underscore — hides it from status bar
    documents = []
    embeddings = []
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            path = os.path.join(pdf_folder, file)
            raw = extract_text_from_pdf(path)
            cleaned = clean_text(raw)
            chunks = chunk_text(cleaned)
            for chunk in chunks[:12]:
                vec = embed_text(chunk)
                documents.append(chunk)
                embeddings.append(vec)
    return documents, embeddings

if not st.session_state.documents:
    placeholder = st.empty()
    placeholder.markdown("""
        <div style="
            background: linear-gradient(135deg, #1F3FD6, #2F5BFF);
            color: white;
            padding: 20px 28px;
            border-radius: 16px;
            font-size: 16px;
            font-weight: 500;
            text-align: center;
            box-shadow: 0 8px 24px rgba(47,91,255,0.3);
            margin: 20px auto;
            max-width: 500px;
        ">
            🦟 &nbsp; Loading FilariaAI knowledge base...<br>
            <span style="font-size:13px; opacity:0.85;">Please wait a moment while we prepare your assistant.</span>
        </div>
    """, unsafe_allow_html=True)
    docs, emb = _load_knowledge_cached("data")
    st.session_state.documents = docs
    st.session_state.embeddings = emb
    placeholder.empty()

# ---------------------------------------------------
# LLM
# ---------------------------------------------------

def ask_llm(context, question):
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "system",
                "content": "You are a public health assistant explaining lymphatic filariasis clearly with bullet points."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ],
        "temperature": 0.2
    }
    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=HEADERS,
        json=payload
    )
    return res.json()["choices"][0]["message"]["content"]

# ---------------------------------------------------
# RAG
# ---------------------------------------------------

def generate_answer(question):
    q_vec = embed_text(question)
    scores = []
    for doc, vec in zip(st.session_state.documents, st.session_state.embeddings):
        score = cosine_similarity(q_vec, vec)
        if score > 0.25:
            scores.append((score, doc))

    if len(scores) == 0:
        return """
⚠️ **This assistant only answers questions related to Lymphatic Filariasis.**

Please ask questions such as:

• What is lymphatic filariasis  
• How does filariasis spread  
• Symptoms of filariasis  
• Mass Drug Administration (MDA)  
• Prevention or treatment of filariasis
"""

    scores.sort(reverse=True)
    context = "\n\n".join([s[1] for s in scores[:3]])
    answer = ask_llm(context, question)
    return clean_answer(answer)

# ---------------------------------------------------
# SIDEBAR QUESTIONS
# ---------------------------------------------------

with st.sidebar:
    for q in examples:
        if st.button(q):
            ts = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({"role": "user", "content": q})
            st.session_state.message_timestamps.append(ts)
            answer = generate_answer(q)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.message_timestamps.append(datetime.now().strftime("%I:%M %p"))
            st.rerun()

# ---------------------------------------------------
# WELCOME MESSAGE (shown only when chat is empty)
# ---------------------------------------------------

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h2>👋 Welcome to FilariaAI! How can I help you today?</h2>
        <p>
            I'm your dedicated assistant for <strong>Lymphatic Filariasis</strong> — a neglected tropical disease
            targeted for elimination by the Government of India.<br><br>
            Ask me anything about its causes, symptoms, prevention, treatment, or the national
            elimination programme. Use the example questions in the sidebar to get started quickly.
        </p>
        <div class="topics">
            <span class="topic-chip">🦟 Disease Overview</span>
            <span class="topic-chip">🔬 Causes & Transmission</span>
            <span class="topic-chip">🩺 Symptoms & Diagnosis</span>
            <span class="topic-chip">💊 MDA Programme</span>
            <span class="topic-chip">🛡️ Prevention</span>
            <span class="topic-chip">🗺️ Affected Regions</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------

# Pad timestamps list if out of sync (safety guard)
while len(st.session_state.message_timestamps) < len(st.session_state.messages):
    st.session_state.message_timestamps.append("")

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        ts = st.session_state.message_timestamps[i] if i < len(st.session_state.message_timestamps) else ""
        if ts:
            st.markdown(f"<div class='msg-timestamp'>{ts}</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------

prompt = st.chat_input("Ask something about Filariasis...")

if prompt:
    ts_user = datetime.now().strftime("%I:%M %p")

    with st.chat_message("user"):
        st.markdown(prompt)
        st.markdown(f"<div class='msg-timestamp'>{ts_user}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    st.session_state.message_timestamps.append(ts_user)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generate_answer(prompt)
        st.markdown(answer)
        ts_bot = datetime.now().strftime("%I:%M %p")
        st.markdown(f"<div class='msg-timestamp'>{ts_bot}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
    st.session_state.message_timestamps.append(ts_bot)
