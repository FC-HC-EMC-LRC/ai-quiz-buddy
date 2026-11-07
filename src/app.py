import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from quiz_logic import calculate_score, parse_quiz_json

load_dotenv()

st.set_page_config(page_title="AI Study & Quiz Buddy", page_icon="📚", layout="centered")
st.title("📚 AI Study & Quiz Buddy")

# Initialize session state variables
if "questions" not in st.session_state:
    st.session_state.questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# API Key lookup: checks Streamlit secrets (cloud), then .env (local)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.warning("Please set the GEMINI_API_KEY environment variable to generate quizzes.")
    st.stop()

client = genai.Client(api_key=api_key)

# Input Section
notes = st.text_area(
    "Enter your study notes or a topic:",
    placeholder="e.g., Photosynthesis is the process used by plants to convert light energy into chemical energy...",
    height=150,
)

num_questions = st.slider("Number of questions:", min_value=2, max_value=5, value=3)

if st.button("Generate Quiz", type="primary"):
    if not notes.strip():
        st.error("Please enter some text before generating.")
    else:
        with st.spinner("Generating quiz questions with AI..."):
            prompt = f"""
            Based on the following notes, generate {num_questions} multiple-choice questions.
            Return ONLY a raw JSON array of objects with no conversational text.
            Each object must strictly match this schema:
            {{
                "question": "string",
                "options": ["string", "string", "string", "string"],
                "answer": "string matching exactly one of the options"
            }}

            Notes:
            {notes}
            """
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                st.session_state.questions = parse_quiz_json(response.text)
                st.session_state.user_answers = {}
                st.session_state.submitted = False
            except ValueError as e:
                st.error(f"Quiz format error: {e}")
            except Exception as e:  # noqa: BLE001
                st.error(f"Failed to generate quiz: {e}")

# Render Quiz Questions
if st.session_state.questions:
    st.write("---")
    st.subheader("Quiz")

    with st.form("quiz_form"):
        for i, q in enumerate(st.session_state.questions):
            st.write(f"**Q{i + 1}: {q['question']}**")
            st.session_state.user_answers[i] = st.radio(
                label=f"Options for Q{i + 1}",
                options=q["options"],
                index=None,
                key=f"q_{i}",
                label_visibility="collapsed",
            )
            st.write("")

        submit_quiz = st.form_submit_button("Submit Answers")

        if submit_quiz:
            st.session_state.submitted = True

    # Show Results
    if st.session_state.submitted:
        correct, total = calculate_score(st.session_state.user_answers, st.session_state.questions)
        st.success(f"### Final Score: {correct} / {total}")

        for i, q in enumerate(st.session_state.questions):
            user_choice = st.session_state.user_answers.get(i)
            if user_choice == q["answer"]:
                st.markdown(f"**Q{i + 1}:** Correct! Selected `{user_choice}`")
            else:
                st.markdown(
                    f"**Q{i + 1}:** Incorrect. You picked `{user_choice}`, correct answer was `{q['answer']}`"
                )