import streamlit as st
import requests

st.set_page_config(page_title="EduTutor AI", layout="wide")

# Simple login screen
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 EduTutor AI Login")
    role = st.selectbox("Select Role", ["student", "educator"])
    user_id = st.text_input("Enter User ID")
    if st.button("Login"):
        if user_id.strip():
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.role = role
        else:
            st.warning("Please enter a valid User ID.")
    st.stop()

# Quiz interface
st.sidebar.title("📚 EduTutor Navigation")
page = st.sidebar.radio("Select page", ["Take Quiz", "Quiz History"])

if page == "Take Quiz":
    st.title("🧠 Take a Quiz")
    topic = st.text_input("Enter Topic")
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
    num_questions = st.slider("Number of Questions", 1, 10, 3)

    if st.button("Generate Quiz"):
        if topic.strip():
            with st.spinner("Generating quiz..."):
                res = requests.post("http://127.0.0.1:8000/generate-quiz/", json={
                    "topic": topic,
                    "difficulty": difficulty,
                    "num_questions": num_questions
                })
                data = res.json()
                st.session_state.quiz = data["questions"]
                st.session_state.answers = data["answers"]
                st.session_state.user_answers = [None] * len(data["questions"])
                st.success("Quiz generated!")
        else:
            st.warning("Please enter a topic.")

    if "quiz" in st.session_state:
        st.subheader("Answer the Questions Below")
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{i+1}: {q}**")
            st.session_state.user_answers[i] = st.radio(
                f"Select your answer for Q{i+1}",
                ["A", "B", "C", "D"],
                key=f"q{i}"
            )

        if st.button("Submit Answers"):
            correct = 0
            total = len(st.session_state.answers)
            for i in range(total):
                if st.session_state.user_answers[i] and st.session_state.user_answers[i].lower() in st.session_state.answers[i].lower():
                    correct += 1
            st.success(f"You got {correct} out of {total} correct!")