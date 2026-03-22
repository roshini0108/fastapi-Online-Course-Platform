# 🎓 LearnHub — FastAPI Online Course Platform

🚀 Final Project for FastAPI Internship  
Built a complete backend system using FastAPI covering real-world API design.

---

## 📌 Project Overview

LearnHub is an online course platform where users can:

- Browse courses
- Enroll in courses
- Add courses to wishlist
- Enroll from wishlist
- Search, filter, sort, and paginate courses

---

## ⚙️ Tech Stack

- Python
- FastAPI
- Pydantic
- Swagger UI (API testing)

---

## 📚 Features Implemented

### 🔹 Day 1 — GET APIs
- Home route
- Get all courses
- Get course by ID
- Course summary

---

### 🔹 Day 2 — POST + Pydantic
- Enrollment API
- Input validation using Pydantic
- Field constraints

---

### 🔹 Day 3 — Helper Functions + Filtering
- `find_course()`
- `calculate_enrollment_fee()`
- Filter courses using query params

---

### 🔹 Day 4 — CRUD Operations
- Add new course (POST)
- Update course (PUT)
- Delete course with business rules (DELETE)

---

### 🔹 Day 5 — Workflow (Wishlist System)
- Add to wishlist
- Remove from wishlist
- Enroll all courses from wishlist

---

### 🔹 Day 6 — Advanced APIs
- Search courses
- Sort courses
- Pagination
- Combined browse endpoint

---

## 🔍 API Endpoints Summary

| Feature | Endpoint |
|--------|---------|
| Home | `/` |
| Get Courses | `/courses` |
| Enroll | `/enrollments` |
| Filter | `/courses/filter` |
| Add Course | `/courses` |
| Update Course | `/courses/{id}` |
| Delete Course | `/courses/{id}` |
| Wishlist | `/wishlist` |
| Search | `/courses/search` |
| Sort | `/courses/sort` |
| Pagination | `/courses/page` |
| Browse | `/courses/browse` |

---

## 🧪 API Testing

All endpoints are tested using Swagger UI:

👉 http://127.0.0.1:8000/docs

---

## 📸 Screenshots

All API outputs are included in the `screenshots/` folder.

---

## 🚀 How to Run

```bash
# Clone repo
git clone <your-repo-link>

# Move into project
cd project-folder

# Create virtual environment
python -m venv skill

# Activate environment
# Windows
skill\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload