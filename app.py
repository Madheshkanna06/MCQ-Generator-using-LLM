import streamlit as st
from groq import Groq
import re
import os

# --------------------------------------
# Load GROQ API KEY from environment variable
# --------------------------------------
api_key ="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"

if not api_key:
    st.error("❌ GROQ_API_KEY not found in environment variables.\n\nPlease set it before running Streamlit.")
    st.stop()

client = Groq(api_key=api_key)

# --------------------------------------
# Streamlit Page Config
# --------------------------------------
st.set_page_config(page_title="MCQ Generator Quiz - Groq", layout="wide")
st.title("🧠 MCQ Generator & Quiz (Groq - Llama 3.3 70B)")

# --------------------------------------
# Input Form
# --------------------------------------
with st.form("mcq_form"):
    subject = st.text_input("Enter subject/topic")
    num_questions = st.number_input("Number of questions", min_value=1, max_value=50, value=5)

    generate_btn = st.form_submit_button("Generate MCQs")

# --------------------------------------
# System Prompt Template
# --------------------------------------
system_prompt = """
You are an expert MCQ generator.
Generate {num_questions} concept-based multiple-choice questions from
the subject "{subject}".

Each question must:
1. Have exactly 4 options labeled A, B, C, D.
2. Include the correct answer at the end in this format:
   Answer: <Correct Option Letter> - <Option Text>
3. Follow this structure:

Q1. <Question>
A) <Option 1>
B) <Option 2>
C) <Option 3>
D) <Option 4>
Answer: B - <Correct Answer>
"""

# --------------------------------------
# Generate MCQs on Button Click
# --------------------------------------
if generate_btn:
    with st.spinner("Generating MCQs using Groq..."):

        prompt = system_prompt.format(subject=subject, num_questions=num_questions)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )

        raw_output = response.choices[0].message.content

    # -----------------------------
    # Parse MCQs
    # -----------------------------
    pattern = r"Q\d+\..*?(?=(?:Q\d+\.|$))"
    questions = re.findall(pattern, raw_output, re.DOTALL)

    if not questions:
        st.error("Failed to parse MCQs. Try again!")
    else:
        st.success("MCQs Generated Successfully!")
        st.session_state["questions"] = questions
        st.session_state["current"] = 0
        st.session_state["score"] = 0


# --------------------------------------
# QUIZ SECTION
# --------------------------------------
if "questions" in st.session_state:

    idx = st.session_state["current"]

    if idx < len(st.session_state["questions"]):

        q = st.session_state["questions"][idx]

        # Extract the answer
        answer_match = re.search(r"Answer:\s*([A-D])\s*-\s*(.*)", q)
        correct_option = answer_match.group(1)
        correct_text = answer_match.group(2)

        # Remove answer line from display
        clean_q = re.sub(r"Answer:.*", "", q).strip()

        st.subheader(f"Question {idx + 1}")
        st.write(clean_q)

        # Answer options
        user_choice = st.radio("Choose answer:", ["A", "B", "C", "D"], index=None)

        if st.button("Submit Answer"):
            if user_choice == correct_option:
                st.success("Correct! 🎉")
                st.session_state["score"] += 1
            else:
                st.error(f"Wrong! Correct Answer: {correct_option} - {correct_text}")

            st.session_state["current"] += 1
            st.rerun()

    else:
        st.success("🎉 Quiz Completed!")
        total = len(st.session_state["questions"])
        score = st.session_state["score"]
        st.write(f"### Your Score: {score}/{total}")
        st.write(f"### Accuracy: {round((score/total)*100, 2)}%")

        if st.button("Restart Quiz"):
            del st.session_state["questions"]
            st.rerun()
