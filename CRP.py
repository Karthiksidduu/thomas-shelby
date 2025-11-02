import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Page Config ----------
st.set_page_config(page_title="Impact College ERP", page_icon="🎓", layout="wide")

# ---------- Session State Initialization ----------
for key, default in {
    "students": [],
    "faculty": [],
    "admins": [],
    "attendance": {},
    "marks": {},
    "fees": {},
    "user": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Authentication ----------
def authenticate(email, password, role):
    if role == "Admin":
        for a in st.session_state.admins:
            if a["email"] == email and a["password"] == password:
                return {**a, "role": "Admin"}

    elif role == "Faculty":
        for f in st.session_state.faculty:
            if f["email"] == email and f["password"] == password:
                return {**f, "role": "Faculty"}

    elif role == "Student":
        for s in st.session_state.students:
            if s["email"] == email and s["password"] == password:
                return {**s, "role": "Student"}

    return None

# ---------- Registration Pages ----------
def register_admin():
    st.title("👑 Admin Registration")
    with st.form("admin_reg_form"):
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        email = st.text_input("Admin Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Set Password", type="password")
        submitted = st.form_submit_button("Register Admin")
        if submitted:
            new_id = f"ADM{len(st.session_state.admins)+1:03d}"
            st.session_state.admins.append({
                "id": new_id,
                "first_name": fname,
                "last_name": lname,
                "email": email,
                "phone": phone,
                "password": password
            })
            st.success(f"✅ Admin {fname} registered successfully!")

def register_student():
    st.title("📝 Student Registration")
    with st.form("student_reg_form"):
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        email = st.text_input("Student Email")
        phone = st.text_input("Phone")
        course = st.text_input("Course")
        semester = st.number_input("Semester", min_value=1, max_value=8, step=1)
        password = st.text_input("Set Password", type="password")
        submitted = st.form_submit_button("Register Student")
        if submitted:
            new_id = f"STU{len(st.session_state.students)+1:03d}"
            st.session_state.students.append({
                "id": new_id,
                "first_name": fname,
                "last_name": lname,
                "email": email,
                "phone": phone,
                "course": course,
                "semester": semester,
                "password": password
            })
            st.session_state.attendance[new_id] = {"present": 0, "total": 0}
            st.session_state.marks[new_id] = {}
            st.session_state.fees[new_id] = {"total": 50000, "paid": 0, "pending": 50000}
            st.success(f"✅ Student {fname} registered successfully!")

def register_faculty():
    st.title("👨‍🏫 Faculty Registration")
    with st.form("faculty_reg_form"):
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        email = st.text_input("Faculty Email")
        phone = st.text_input("Phone Number")
        dept = st.text_input("Department")
        subjects = st.text_area("Subjects (comma-separated)")
        password = st.text_input("Set Password", type="password")
        submitted = st.form_submit_button("Register Faculty")
        if submitted:
            new_id = f"FAC{len(st.session_state.faculty)+1:03d}"
            st.session_state.faculty.append({
                "id": new_id,
                "first_name": fname,
                "last_name": lname,
                "email": email,
                "phone": phone,
                "department": dept,
                "subjects": [s.strip() for s in subjects.split(",") if s.strip()],
                "password": password
            })
            st.success(f"✅ Faculty {fname} registered successfully!")

# ---------- Login Page ----------
def login_page():
    st.markdown("<h1 style='text-align:center;'>🎓 Impact College ERP</h1>", unsafe_allow_html=True)
    st.write("## Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Student", "Faculty", "Admin"])

    if st.button("Sign In"):
        user = authenticate(email, password, role)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

# ---------- Dashboards ----------
def admin_dashboard():
    user = st.session_state.user
    st.title(f"👑 Welcome, {user['first_name']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", len(st.session_state.students))
    col2.metric("Total Faculty", len(st.session_state.faculty))
    col3.metric("Courses", len(set(s["course"] for s in st.session_state.students)))

    st.write("### Overall Attendance")
    if st.session_state.students:
        labels = [s["first_name"] for s in st.session_state.students]
        values = [
            (st.session_state.attendance[s["id"]]["present"] / st.session_state.attendance[s["id"]]["total"]) * 100
            if st.session_state.attendance[s["id"]]["total"] > 0 else 0
            for s in st.session_state.students
        ]
        fig, ax = plt.subplots()
        ax.bar(labels, values, color="skyblue")
        ax.set_ylabel("Attendance %")
        ax.set_ylim(0, 100)
        st.pyplot(fig)
    else:
        st.info("No students registered yet.")

def faculty_dashboard():
    f = st.session_state.user
    st.title(f"👩‍🏫 Welcome, {f['first_name']} {f['last_name']}")
    st.write(f"Department: {f['department']}")
    st.write("Subjects:", ", ".join(f["subjects"]))

    st.subheader("📌 Mark Attendance")
    if not st.session_state.students:
        st.info("No students available.")
        return

    student_choice = st.selectbox("Select Student", [s["first_name"] for s in st.session_state.students])
    if st.button("Mark Present"):
        student = next(s for s in st.session_state.students if s["first_name"] == student_choice)
        att = st.session_state.attendance[student["id"]]
        att["present"] += 1
        att["total"] += 1
        st.success(f"✅ Attendance marked for {student_choice}")

def student_dashboard():
    s = st.session_state.user
    st.title(f"👨‍🎓 Welcome, {s['first_name']} {s['last_name']}")
    st.write(f"Course: {s['course']} | Semester: {s['semester']}")

    st.subheader("📊 Attendance")
    att = st.session_state.attendance[s["id"]]
    percent = (att["present"] / att["total"] * 100) if att["total"] > 0 else 0
    st.progress(int(percent))
    st.write(f"Attendance: {att['present']} / {att['total']} ({percent:.1f}%)")

    st.subheader("📝 Marks")
    marks_df = pd.DataFrame(st.session_state.marks[s["id"]].items(), columns=["Subject", "Marks"])
    st.table(marks_df if not marks_df.empty else pd.DataFrame(columns=["Subject", "Marks"]))

    st.subheader("💰 Fees")
    f = st.session_state.fees[s["id"]]
    st.write(f"Total: ₹{f['total']} | Paid: ₹{f['paid']} | Pending: ₹{f['pending']}")

# ---------- Main ----------
if st.session_state.user is None:
    menu = st.sidebar.radio("Navigation", ["Login", "Register Student", "Register Faculty", "Register Admin"])
    if menu == "Login":
        login_page()
    elif menu == "Register Student":
        register_student()
    elif menu == "Register Faculty":
        register_faculty()
    elif menu == "Register Admin":
        register_admin()
else:
    user = st.session_state.user
    st.sidebar.title(f"{user['role']} Menu")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    if user["role"] == "Admin":
        admin_dashboard()
    elif user["role"] == "Faculty":
        faculty_dashboard()
    elif user["role"] == "Student":
        student_dashboard()