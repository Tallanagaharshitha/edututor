import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import streamlit as st
import requests
from PIL import Image
import base64
from quiz_generator import generate_quiz
from datetime import datetime
import os
import json

# Page config
st.set_page_config(page_title="EduTutor AI", layout="wide")

# Dummy course data
courses_list = [
    {"title": "Introduction to AI", "description": "Basics of Artificial Intelligence"},
    {"title": "Python Programming", "description": "Learn the fundamentals of Python"},
    {"title": "Data Structures", "description": "Understand how data is organized"},
]

course_details = {
    "Introduction to AI": "Artificial Intelligence (AI) is the simulation of human intelligence in machines. It includes tasks like learning, reasoning, problem-solving, and decision-making. AI powers virtual assistants, self-driving cars, and intelligent recommendations across many industries.",
    "Python Programming": "Python is a versatile, high-level programming language. It is known for its readability and vast ecosystem of libraries, making it perfect for data analysis, web development, AI, and more.",
    "Data Structures": "Data structures are organized ways of storing data for efficient access and modification. Examples include arrays, linked lists, stacks, queues, trees, and graphs—each suitable for different types of problems."
}

# Background image base64 function
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Session state init
if "get_started" not in st.session_state:
    st.session_state.get_started = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.quiz_history = []
    st.session_state.registered_users = {}
    st.session_state.students = {}
    st.session_state.user_profile = {"name": "", "bio": "", "profile_pic": None}
if "expanded_course" not in st.session_state:
    st.session_state.expanded_course = None
if "model" not in st.session_state:
    st.session_state.model = None
if "tokenizer" not in st.session_state:
    st.session_state.tokenizer = None
if "device" not in st.session_state:
    st.session_state.device = None

# ------------------ GET STARTED PAGE ------------------
if not st.session_state.get_started:
    bg_image_base64 = get_base64_image("bg.png")
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Curlz+MT&display=swap');
        .stApp {{
            background-image: url("data:image/png;base64,{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .getstarted-container {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}
        .getstarted-title {{
            font-family: 'Curlz MT', cursive;
            font-size: 72px;
            color: white;
            text-shadow: 2px 2px #00000080;
            margin-bottom: 30px;
        }}
        </style>

        <div class='getstarted-container'>
            <div class='getstarted-title'>EduTutor AI</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div style='margin-top: 20px;'>""", unsafe_allow_html=True)
    centered = st.columns([4, 2, 4])
    with centered[1]:
        if st.button("🚀 Get Started"):
            st.session_state.get_started = True
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ------------------ LOGIN / REGISTER ------------------
if not st.session_state.logged_in:
    st.title("🔐 EduTutor AI Login/Register")
    role = st.selectbox("Select Role", ["student", "educator"])
    action = st.radio("Action", ["Login", "Register"])
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if action == "Register" and st.button("Register"):
        if user_id and password:
            key = f"{role}:{user_id}"
            st.session_state.registered_users[key] = password
            st.success("Registered successfully!")
        else:
            st.warning("Fill both fields!")

    if action == "Login" and st.button("Login"):
        key = f"{role}:{user_id}"
        if st.session_state.registered_users.get(key) == password:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.user_id = user_id
            if role == "student" and user_id not in st.session_state.students:
                st.session_state.students[user_id] = []
        else:
            st.error("Invalid credentials.")
    st.stop()

# ------------------ STUDENT ------------------
if st.session_state.role == "student":
    st.sidebar.title("🎓 Student Panel")
    choice = st.sidebar.radio("Navigate", ["Dashboard", "Take Quiz", "Quiz History", "Courses"])

    if choice == "Dashboard":
        st.title(f"Welcome, {st.session_state.user_id}")
        st.subheader("🧑 Your Profile")
        uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "png"])
        if uploaded_file:
            st.session_state.user_profile["profile_pic"] = uploaded_file
        name = st.text_input("Full Name", value=st.session_state.user_profile.get("name", ""))
        bio = st.text_area("About You", value=st.session_state.user_profile.get("bio", ""))
        if st.button("Update Profile"):
            st.session_state.user_profile["name"] = name
            st.session_state.user_profile["bio"] = bio
            st.success("Profile updated!")
        if st.session_state.user_profile["profile_pic"]:
            st.image(st.session_state.user_profile["profile_pic"], width=150, caption="Profile Picture")
        st.write("Name:", st.session_state.user_profile.get("name", ""))
        st.write("About:", st.session_state.user_profile.get("bio", ""))

    elif choice == "Take Quiz":
        if st.session_state.model is None:
            with st.spinner("Loading model..."):
                from model_setup import load_model_and_tokenizer
                st.session_state.model, st.session_state.tokenizer, st.session_state.device = load_model_and_tokenizer()

        st.header("📘 Generate a Quiz")
        text_input = st.text_input("Enter Topic or Text for Quiz")
        level = st.selectbox("Select Level", ["easy", "medium", "hard"])
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)

        if "quiz" not in st.session_state:
            st.session_state.quiz = None
        if "answers" not in st.session_state:
            st.session_state.answers = {}

        if st.button("Generate Quiz"):
            if text_input.strip():
                with st.spinner("Generating quiz..."):
                    quiz = generate_quiz(
                        text_input,
                        level,
                        st.session_state.model,
                        st.session_state.tokenizer,
                        st.session_state.device
                    )
                    st.session_state.quiz = quiz
                    st.session_state.answers = {}
                    st.success("✅ Quiz generated successfully!")
            else:
                st.warning("⚠ Please enter a topic.")

        if st.session_state.quiz:
            st.subheader("📝 Take the Quiz")
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz):
                    st.write(f"*Q{i+1}: {q['question']}*")
                    st.session_state.answers[str(i)] = st.radio(
                        label="Choose your answer:",
                        options=q["options"],
                        key=f"answer_{i}"
                    )
                submitted = st.form_submit_button("Submit")

            if submitted:
                score = 0
                st.subheader("📊 Quiz Results")
                for i, q in enumerate(st.session_state.quiz):
                    user_ans = st.session_state.answers.get(str(i))
                    correct_ans = q["answer"]
                    is_correct = user_ans == correct_ans
                    if is_correct:
                        score += 1
                    st.markdown(f"*Q{i+1}: {q['question']}*")
                    st.write(f"Your Answer: {user_ans}")
                    st.write(f"✅ Correct Answer: {correct_ans}")
                    st.success("Correct!") if is_correct else st.error("Incorrect.")

                st.info(f"🏁 Final Score: {score} / {len(st.session_state.quiz)}")

                quiz_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                RESULTS_FILE = "quiz_results.json"
                if os.path.exists(RESULTS_FILE):
                    with open(RESULTS_FILE, "r") as f:
                        results = json.load(f)
                else:
                    results = {}

                results[quiz_id] = {
                    "user_id": st.session_state.user_id,
                    "quiz_id": quiz_id,
                    "topic": text_input,
                    "score": score,
                    "total": len(st.session_state.quiz),
                    "timestamp": datetime.now().isoformat()
                }

                with open(RESULTS_FILE, "w") as f:
                    json.dump(results, f, indent=2)

                st.session_state.quiz = None
                st.session_state.answers = {}

    elif choice == "Quiz History":
        st.title("📜 Quiz History")
        for q in st.session_state.quiz_history:
            st.write(f"📘 {q['topic']} - Score: {q['score']}")

    elif choice == "Courses":
        st.title("📚 Available Courses")
        left_col, right_col = st.columns([2, 2])

        with left_col:
            for idx, course in enumerate(courses_list):
                col1, col2 = st.columns([6, 1.5])
                with col1:
                    st.subheader(course["title"])
                    st.markdown(f"{course['description']}")
                with col2:
                    if st.session_state.expanded_course == course["title"]:
                        if st.button("❌ Close", key=f"close_{idx}"):
                            st.session_state.expanded_course = None
                            st.rerun()
                    else:
                        if st.button("🔍 See More", key=f"see_{idx}"):
                            st.session_state.expanded_course = course["title"]
                            st.rerun()

        with right_col:
            selected = st.session_state.expanded_course
            if selected:
                st.markdown(f"""
                    <div style='background-color:#f9f9f9; padding:20px; border-radius:10px; border:1px solid #ccc;'>
                        <h4>{selected}</h4>
                        <p>{course_details[selected]}</p>
                """, unsafe_allow_html=True)

                if selected == "Introduction to AI":
                    st.markdown("[📘 Learn Here (AI Intro - YouTube)](https://youtu.be/2ePf9rue1Ao)")
                    st.markdown("[📗 AI Course - Coursera](https://www.coursera.org/learn/introduction-to-ai)")
                elif selected == "Python Programming":
                    st.markdown("[📘 Learn Here (Python Basics)](https://youtu.be/rfscVS0vtbw)")
                    st.markdown("[📗 Python - W3Schools](https://www.w3schools.com/python/)")
                elif selected == "Data Structures":
                    st.markdown("[📘 Learn Here (Data Structures)](https://youtu.be/sVxBVvlnJsM)")
                    st.markdown("[📗 GeeksForGeeks - DS](https://www.geeksforgeeks.org/data-structures/)")

                st.markdown("</div>", unsafe_allow_html=True)

# ------------------ EDUCATOR ------------------
elif st.session_state.role == "educator":
    st.sidebar.title("👩‍🏫 Educator Panel")
    option = st.sidebar.radio("Navigate", ["Dashboard", "Student Activity"])

    if option == "Dashboard":
        st.title(f"Welcome Educator {st.session_state.user_id}")
        st.info("Here you can manage students and monitor activity.")

    elif option == "Student Activity":
        st.title("📊 Student Activity Monitor")
        if not st.session_state.students:
            st.warning("No student activity yet.")
        else:
            for student, records in st.session_state.students.items():
                st.subheader(f"👤 {student}")
                if not records:
                    st.markdown("No quizzes taken yet.")
                else:
                    for rec in records:
                        st.write(f"📝 Topic: {rec['topic']}, Score: *{rec['score']}*")