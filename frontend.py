import streamlit as st
import requests


BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="RecruitIQ Dashboard", layout="wide")

st.title("RecruitIQ - AI Interview Dashboard")
# -------- HANDLE INTERVIEW LINK --------
query_params = st.query_params
interview_id_from_url = query_params.get("interview_id")

# 🔐 LOGIN
st.sidebar.header("Login")

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })

    if res.status_code == 200:
        st.session_state["token"] = res.json()["access_token"]
        st.success("Login successful")
    else:
        st.error("Login failed")

if "token" not in st.session_state:
    st.warning("Please login first")
    st.stop()

headers = {
    "Authorization": f"Bearer {st.session_state['token']}"
}

# 🔄 NAVIGATION
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Candidates", "Add Candidate"]
)

# ================= DASHBOARD =================
if page == "Dashboard":

    st.header("Dashboard")

    if st.button("Refresh Data"):
        res = requests.get(f"{BASE_URL}/candidates/", headers=headers)
        if res.status_code == 200:
            st.session_state["candidates"] = res.json()
        else:
            st.error("Failed to fetch candidates")

    if "candidates" in st.session_state:

        candidates = st.session_state["candidates"]

        total = len(candidates)
        screening = sum(1 for c in candidates if c["status"] == "SCREENING")
        completed = sum(1 for c in candidates if c["status"] == "INTERVIEW_COMPLETED")
        new = sum(1 for c in candidates if c["status"] == "NEW")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Candidates", total)
        col2.metric("Screening", screening)
        col3.metric("Interview Completed", completed)
        col4.metric("New", new)

    else:
        st.info("Click 'Refresh Data' to load candidates")

# ================= CANDIDATES =================
if page == "Candidates":

    st.subheader("Candidate List")

    # ✅ LOAD BUTTON (prevents crash)
    if "candidates" not in st.session_state:
        if st.button("Load Candidates"):
            res = requests.get(f"{BASE_URL}/candidates/", headers=headers)

            if res.status_code == 200:
                st.session_state["candidates"] = res.json()
            else:
                st.error("Failed to fetch candidates")

        st.stop()

    # ✅ CARD UI
    for c in st.session_state["candidates"]:

        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"### {c['full_name']}")
                st.caption(c["email"])

            with col2:
                status = c["status"]

                if status == "NEW":
                    st.warning(f"Status: {status}")
                elif status == "SCREENING":
                    st.info(f"Status: {status}")
                elif status == "INTERVIEW_COMPLETED":
                    st.success(f"Status: {status}")
                else:
                    st.write(f"Status: {status}")

            with col3:
                if st.button("View", key=f"view_{c['id']}"):
                    res = requests.get(
                        f"{BASE_URL}/candidates/{c['id']}",
                        headers=headers
                    )

                    if res.status_code == 200:
                        st.session_state["selected_candidate"] = res.json()
                    else:
                        st.error("Failed to fetch details")

            st.divider()

# ================= CANDIDATE DETAILS =================
if "selected_candidate" in st.session_state:

    data = st.session_state["selected_candidate"]

    st.divider()
    st.header("Candidate Details")

    st.subheader(data["full_name"])
    st.write("Email:", data["email"])
    st.write("Status:", data["status"])

    tab1, tab2, tab3 = st.tabs(["Resume", "Parsed Data", "Interview Report"])

    with tab1:
        if data.get("resume"):
            st.success("Resume available")
        else:
            st.warning("No resume uploaded")

    with tab2:
        resume = data.get("resume")

        if resume:
            st.write("### Skills")
            st.write(", ".join(resume.get("skills", [])))

            st.write("### Education")
            for edu in resume.get("education", []):
                st.write(f"- {edu.get('degree')}")

            st.write("### Projects")
            for proj in resume.get("projects", []):
                st.write(f"**{proj.get('title')}**")
                st.write(proj.get("description"))
                st.write("---")
        else:
            st.warning("No parsed data available")

    with tab3:
        report = data.get("interview_report")

        if report:
            st.metric("Score", report.get("overall_score"))
            st.success(report.get("recommendation"))
            st.write("### Strengths")
            st.write(report.get("strengths"))
            st.write("### Weaknesses")
            st.write(report.get("weaknesses"))
        else:
            st.warning("No interview report yet")

# -------- UPLOAD RESUME --------
    st.subheader("Resume")

    if data.get("resume"):
        st.success("Resume already uploaded")
    else:
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

        if uploaded_file:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            res = requests.post(
            f"{BASE_URL}/resumes/resume",
            params={"candidate_id": data["id"]},   # ✅ THIS IS IMPORTANT
            files=files,
            headers=headers
        )

            if res.status_code == 200:

                resume_id = res.json().get("id")

                parse_res = requests.post(
                    f"{BASE_URL}/resumes/{resume_id}/parse",
                    headers=headers
                )

                if parse_res.status_code == 200:
                    st.success("Resume uploaded & parsed")

                    refreshed = requests.get(
                        f"{BASE_URL}/candidates/{data['id']}",
                        headers=headers
                    )
                    if refreshed.status_code == 200:
                        st.session_state["selected_candidate"] = refreshed.json()
                else:
                    st.error(f"Parsing failed: {parse_res.text}")

            else:
                st.error(res.text)
    if interview_id_from_url:

        st.title("Candidate Interview")

        if "interview" not in st.session_state:
        # fetch interview first question
            res = requests.get(
                f"{BASE_URL}/interviews/{interview_id_from_url}",
                headers=headers
            )

            if res.status_code == 200:
                data = res.json()

                st.session_state["interview"] = {
                    "id": interview_id_from_url,
                    "question": data.get("question")
                }
            else:
                st.error("Invalid interview link")
                st.stop()

        st.write("### Question:")
        st.write(st.session_state["interview"]["question"])

        answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):

        res = requests.post(
            f"{BASE_URL}/interviews/{interview_id_from_url}/answer",
            json={"answer": answer}
        )

        if res.status_code == 200:
            result = res.json()

            if result.get("interview_completed"):
                st.success("Interview Completed")

                report = result.get("report")
                st.write("### Result")
                st.write(report)

                del st.session_state["interview"]
            else:
                st.session_state["interview"]["question"] = result.get("next_question")
        else:
            st.error(res.text)

    st.stop()
    
    # -------- START INTERVIEW --------
    st.subheader("Interview")

    if data.get("status") == "INTERVIEW_COMPLETED":
        st.success("Interview already completed")
    else:
        if st.button("Start Interview"):
            res = requests.post(
                f"{BASE_URL}/interviews/start",
                json={
                    "candidate_id": data["id"],
                    "job_role": "Software Engineer",
                    "experience_level": "Junior"
                },
                headers=headers
            )

            if res.status_code == 200:
                print("INTERVIEW RESPONSE:", res.json())
                interview_data = res.json()

                st.session_state["interview"] = {
                    "id": interview_data["interview_id"],
                    "question": interview_data.get("question") or interview_data.get("first_question")
                }

                st.success("Interview started")

                link = f"http://localhost:8501/?interview_id={interview_data['interview_id']}"

                st.write("### Share this link with candidate:")
                st.code(link)
            else:
                st.error(res.text)
# ================= INTERVIEW =================
if "interview" in st.session_state:

    st.subheader("Interview in Progress")

    st.write("### Question:")
    st.write(st.session_state["interview"]["question"])

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):

        res = requests.post(
            f"{BASE_URL}/interviews/{st.session_state['interview']['id']}/answer",
            json={"answer": answer},
            headers=headers
        )

        if res.status_code == 200:
            result = res.json()

            if result.get("interview_completed"):
                st.success("Interview Completed")
                st.session_state["report"] = result.get("report")
                del st.session_state["interview"]
            else:
                st.session_state["interview"]["question"] = result.get("next_question")
        else:
            st.error(res.text)

# ================= REPORT =================
if "report" in st.session_state:

    report = st.session_state["report"]

    st.divider()
    st.header("Final Interview Report")

    st.metric("Overall Score", report.get("overall_score"))
    st.success(report.get("recommendation"))

    st.write("### Strengths")
    st.write(report.get("strengths"))

    st.write("### Weaknesses")
    st.write(report.get("weaknesses"))

# ================= ADD CANDIDATE =================
if page == "Add Candidate":

    st.header("Add Candidate")

    name = st.text_input("Full Name")
    email_input = st.text_input("Email")
    phone = st.text_input("Phone")
    role = st.text_input("Current Role")
    exp = st.number_input("Experience", min_value=0.0)
    location = st.text_input("Location")
    source = st.text_input("Source")

    if st.button("Create Candidate"):
        res = requests.post(
            f"{BASE_URL}/candidates/",
            json={
                "full_name": name,
                "email": email_input,
                "phone": phone,
                "current_role": role,
                "experience_years": exp,
                "location": location,
                "source": source
            },
            headers=headers
        )

        if res.status_code == 200:
            st.success("Candidate created")
        else:
            st.error(res.text)