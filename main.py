import streamlit as st
import requests
from langdetect import detect
from datetime import datetime
from PyPDF2 import PdfReader

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="EchoCast AI 🎙",
    page_icon="🎙",
    layout="wide"
)

# ------------------ API KEY CHECK ------------------
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("❌ OPENROUTER_API_KEY not found in Streamlit Secrets.")
    st.stop()

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# ------------------ HEADER ------------------
st.title("🎙 EchoCast AI – Multimodal & Multilingual Podcast Synthesis Agent")
st.caption(
    "Accepts Text • PDF • Audio • Video | Processes as Text | Auto-download Output"
)

# ------------------ SIDEBAR ------------------
st.sidebar.header("🎛 Podcast Controls")

topic = st.sidebar.text_input("Topic (Optional)", "Trending News & Insights")

tone = st.sidebar.selectbox(
    "Tone",
    ["Casual", "Formal", "Deep Dive"]
)

length = st.sidebar.selectbox(
    "Length",
    ["Short (1–2 mins)", "Medium (3–5 mins)", "Long (6–8 mins)"]
)

audience = st.sidebar.selectbox(
    "Audience",
    ["Students", "Creators", "General Public"]
)

output_language = st.sidebar.text_input(
    "Output Language",
    "English"
)

# ------------------ INPUT SECTION ------------------
st.subheader("🧩 Multimodal Input")

written_text = st.text_area(
    "📝 Write / Paste Text (Any Language)",
    height=160
)

uploaded_pdf = st.file_uploader(
    "📄 Upload PDF",
    type=["pdf"]
)

uploaded_audio = st.file_uploader(
    "🔊 Upload Audio (mp3 / wav)",
    type=["mp3", "wav"]
)

uploaded_video = st.file_uploader(
    "🎥 Upload Video (mp4 / mov)",
    type=["mp4", "mov"]
)

st.markdown("### 📝 Transcript (Required for Audio / Video)")
transcript_text = st.text_area(
    "Paste transcript for audio/video files (required for free API)",
    height=140
)

# ------------------ INPUT PROCESSING ------------------
combined_text = ""

if written_text:
    combined_text += written_text + "\n"

if uploaded_pdf:
    reader = PdfReader(uploaded_pdf)
    for page in reader.pages:
        combined_text += page.extract_text() + "\n"

if uploaded_audio:
    combined_text += f"\n[Audio Uploaded: {uploaded_audio.name}]\n"
    combined_text += transcript_text + "\n"

if uploaded_video:
    combined_text += f"\n[Video Uploaded: {uploaded_video.name}]\n"
    combined_text += transcript_text + "\n"

# ------------------ GENERATE BUTTON ------------------
generate = st.button("🚀 Generate Podcast Script")

# ------------------ OPENROUTER CALL ------------------
def generate_podcast(system_prompt, user_prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "EchoCast AI"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

# ------------------ AI PIPELINE ------------------
if generate and combined_text.strip():

    with st.spinner("🧠 EchoCast AI agents are synthesizing content..."):

        detected_language = detect(combined_text)

        system_prompt = f"""
You are EchoCast AI, a multi-agent news-to-podcast synthesis system.

Agents:
1. News Analyst
2. Fact Extractor
3. Podcast Script Writer
4. Editor

Rules:
- Input may come from text, PDF, audio transcript, or video transcript
- Output must be TEXT only
- Final language: {output_language}
- Create podcast-style narration with intro & outro
"""

        user_prompt = f"""
Topic: {topic}
Detected Input Language: {detected_language}
Audience: {audience}
Tone: {tone}
Length: {length}

Content:
{combined_text}

Steps:
1. Extract key facts
2. Summarize clearly
3. Convert into engaging podcast narration
"""

        podcast_script = generate_podcast(system_prompt, user_prompt)

    # ------------------ OUTPUT ------------------
    st.subheader("🎧 Podcast Script (Text Output)")

    st.text_area(
        "Generated Script",
        podcast_script,
        height=420
    )

    filename = f"EchoCast_Podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    st.download_button(
        "⬇️ Download Podcast Script",
        podcast_script,
        file_name=filename,
        mime="text/plain"
    )

    st.success("✅ Podcast script generated successfully!")

else:
    st.info("ℹ️ Upload content or provide text to generate output.")
