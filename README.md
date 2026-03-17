# 🎓 Smart Student Progress Tracker
> An AI-driven educational ecosystem featuring Predictive Analytics for Student Success.

---

## 🌟 Project Overview
**Smart Student Progress Tracker** is a full-stack Flask application designed to bridge the gap between data and education. By analyzing attendance, syllabus coverage, and historical marks, the system provides real-time "At-Risk" predictions to help teachers intervene early.

## 🧠 The AI Engine (Random Forest)
The core of this project is a **Machine Learning Model** trained on 1,200 synthetic data points to simulate realistic classroom trends.
- **Algorithm:** Random Forest Regressor
- **Features:** Attendance Rate %, Syllabus Progress (Weak/Average/Best), and Historical Performance.
- **Goal:** Predict the next test score to identify students needing extra support.

---

## 📸 System Walkthrough

### 👩‍🏫 Teacher Dashboard (AI-Powered)
*Analyze performance trends and view automated grade predictions.*
<p align="center">
  <img src="images/teacher/Screenshot 2026-03-09 at 2.53.23 PM.png" width="45%">
</p>

### 👨‍👩‍👦 Parent Portal
*Real-time access to child's attendance and academic growth.*
<p align="center">
  <img src="images/parent/Screenshot 2026-03-09 at 3.10.56 PM.png" width="60%">
</p>

### 🔑 Admin Control Center
*Centralized management of Users (RBAC), Classes, and Subjects.*
<p align="center">
  <img src="images/admin/Screenshot 2026-03-09 at 3.10.04 PM.png" width="60%">
</p>

---

## 🛠️ Tech Stack
- **Backend:** Python (Flask)
- **Database:** SQLAlchemy (SQLite/PostgreSQL)
- **AI/ML:** Scikit-Learn, Pandas, Joblib
- **Frontend:** HTML5, CSS3 (Bootstrap), JavaScript
- **Version Control:** Git & GitHub

## 🚀 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/Smart-Student-Progress-Tracker.git](https://github.com/YOUR_USERNAME/Smart-Student-Progress-Tracker.git)
   cd Smart-Student-Progress-Tracker


## 📁 Project Structure
```text
├── app.py              # Main Flask application
├── models.py           # SQLAlchemy Database models
├── train_model.py      # ML Training script (1,200 records)
├── student_model.pkl   # The trained AI brain
├── ai_logic.py         # Bridge between DB and ML
└── templates/          # HTML Dashboards