from unicodedata import category
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import HTTPException
from fastapi import Query
app = FastAPI()
courses=[
    {"id":1,"title":"Full Stack Web Development","instructor":"John Doe","category":"Web Dev","level":"Beginner","price":99,"seats_left":20},
    {"id":2,"title":"Backend APIs with FastAPI","instructor":"Jane Smith","category":"Web Dev","level":"Advanced","price":299,"seats_left":15},
    {"id":3,"title":"Machine Learning Fundamentals","instructor":"Bob Johnson","category":"Data Science","level":"Intermediate","price":199,"seats_left":10},
    {"id":4,"title":"Figma for Beginners","instructor":"Alice Williams","category":"Design","level":"Intermediate","price":199,"seats_left":5},
    {"id":5,"title":"Docker & Kubernetes Basics","instructor":"Charlie Brown","category":"DevOps","level":"Beginner","price":99,"seats_left":25},
    {"id":6,"title":"Linux for DevOps Engineers","instructor":"David Davis","category":"DevOps","level":"Advanced","price":299,"seats_left":20}
]

enrollments = []
enrollment_counter = 1

wishlist = []

class EnrollRequest(BaseModel):
    student_name: str = Field(..., min_length=2)
    course_id: int = Field(..., gt=0)
    email: str = Field(..., min_length=5)
    payment_method: str = "card"
    coupon_code: str = ""
    gift_enrollment: bool = False
    recipient_name: str = ""

class NewCourse(BaseModel):
    title: str = Field(..., min_length=2)
    instructor: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    level: str = Field(..., min_length=2)
    price: float = Field(..., ge=0)
    seats_left: int = Field(..., gt=0)

class WishlistEnrollRequest(BaseModel):
    student_name: str
    payment_method: str

def find_course(course_id):
    for course in courses:
        if course["id"] == course_id:
            return course
    return None

def calculate_enrollment_fee(price, seats_left, coupon_code):
    fprice = price  
    if seats_left > 5:
        fprice = fprice * 0.9
    if coupon_code == "STUDENT20":
        fprice = fprice * 0.8
    elif coupon_code == "FLAT500":
        fprice = fprice - 500
    return fprice

@app.get("/")
def home():
    return {"message": "Welcome to LearnHub Online Courses"}

@app.get("/courses")
def get_courses():
    return {"courses": courses, "total": len(courses), "total_seats_available": sum(course["seats_left"] for course in courses)}

@app.get("/enrollments")
def get_enrollments():
    return {"enrollments": enrollments, "total": len(enrollments)}

@app.get("/courses/summary")
def get_course_summary():
    return {
  "total_courses": len(courses),
  "free_courses": len([course for course in courses if course["price"] == 0]),
  "most_expensive_course": max(courses, key=lambda x: x["price"]) if courses else None,
  "total_seats": sum(course["seats_left"] for course in courses),
  "category_count": {category: len([course for course in courses if course["category"] == category]) for category in set(course["category"] for course in courses)}
}

@app.post("/test-enroll")
def test_enroll(data: EnrollRequest):
    return {"message": "ok"}

@app.post("/enrollments")
def enroll(data: EnrollRequest):
    global enrollment_counter
    if data.gift_enrollment and data.recipient_name == "":
        raise HTTPException(status_code=400, detail="Recipient name is required for gift enrollments")
    course = find_course(data.course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if course["seats_left"] <= 0:
        raise HTTPException(status_code=400, detail="No seats available for this course")
    final_fee = calculate_enrollment_fee(
    course["price"],
    course["seats_left"],
    data.coupon_code
    )
    course["seats_left"] -= 1
    record = {
    "enrollment_id": enrollment_counter,
    "student_name": data.student_name,
    "course_title": course['title'],
    "instructor": course['instructor'],
    "original_price": course['price'],
    "final_fee": final_fee,
    "gift_enrollment": data.gift_enrollment,
    "recipient_name": data.recipient_name if data.gift_enrollment else None
    }
    enrollments.append(record)
    enrollment_counter += 1 
    return {"message": "Enrollment successful", "enrollment": record}

@app.get("/courses/filter")
def filter_courses(
    category: str = Query(None, description="Filter by course category"),
    level: str = Query(None, description="Filter by course level"),
    max_price: float = Query(None, description="Maximum price"),
    has_seats: bool = Query(None, description="Filter by seat availability")
):
    filtered_courses = courses
    if category is not None:
        filtered_courses = [course for course in filtered_courses if course["category"].lower() == category.lower()]
    if level is not None:
        filtered_courses = [course for course in filtered_courses if course["level"].lower() == level.lower()]
    if max_price is not None:
        filtered_courses = [course for course in filtered_courses if course["price"] <= max_price]
    if has_seats is not None:
        if has_seats:
            filtered_courses = [course for course in filtered_courses if course["seats_left"] > 0]
        else:
            filtered_courses = [course for course in filtered_courses if course["seats_left"] == 0]
    return {"filtered_courses": filtered_courses, "total": len(filtered_courses)}

@app.post("/courses", status_code=201)
def add_course(course: NewCourse):
    for c in courses:
        if c["title"].lower() == course.title.lower():
            raise HTTPException(status_code=400, detail="Course with this title already exists")
    new_course = course.dict()
    new_course["id"] = max(c["id"] for c in courses) + 1 if courses else 1
    courses.append(new_course)
    return {"message": "Course added successfully", "course": new_course}

@app.put("/courses/{course_id}")
def update_course(
    course_id: int,
    price: int = Query(None),
    seats_left: int = Query(None)
):
    for c in courses:
        if c["id"] == course_id:

            # Update only provided fields
            if price is not None:
                c["price"] = price

            if seats_left is not None:
                c["seats_left"] = seats_left

            return {
                "message": "Course updated successfully",
                "course": c
            }

    raise HTTPException(status_code=404, detail="Course not found")

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    for c in courses:
        if c["id"] == course_id:
            for e in enrollments:
                if e["course_title"] == c["title"]:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot delete course with active enrollments"
                    )
            courses.remove(c)
            return {"message": "Course deleted successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

@app.post("/wishlist/add")
def add_to_wishlist(student_name: str, course_id: int):
    course = find_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    for w in wishlist:
        if w["student_name"] == student_name and w["course_id"] == course_id:
            raise HTTPException(status_code=400, detail="Course already in wishlist")
    wishlist.append({
        "student_name": student_name,
        "course_id": course_id,
        "course_title": course["title"]
    })
    return {"message": "Course added to wishlist"}

@app.get("/wishlist")
def get_wishlist(student_name: str):
    filtered = [item for item in wishlist if item["student_name"] == student_name]
    total_value = 0
    for item in filtered:
        course = find_course(item["course_id"])
        if course:
            total_value += course["price"]
    return {
        "wishlist": filtered,
        "total_value": total_value
    }

@app.post("/wishlist/enroll-all")
def enroll_all(data: WishlistEnrollRequest):
    global enrollment_counter
    student_items = [item for item in wishlist if item["student_name"] == data.student_name]
    if not student_items:
        raise HTTPException(status_code=404, detail="No wishlist items found for this student")
    enrolled = []
    total_fee = 0
    for item in student_items:
        course = find_course(item["course_id"])
        if course is None:
            continue
        if course["seats_left"] <= 0:
            continue
        final_fee = calculate_enrollment_fee(
            course["price"],
            course["seats_left"],
            ""   
        )
        course["seats_left"] -= 1
        record = {
            "enrollment_id": enrollment_counter,
            "student_name": data.student_name,
            "course_title": course["title"],
            "instructor": course["instructor"],
            "original_price": course["price"],
            "final_fee": final_fee
        }
        enrollments.append(record)
        enrolled.append(record)
        enrollment_counter += 1
        total_fee += final_fee
    global wishlist
    wishlist = [item for item in wishlist if item["student_name"] != data.student_name]
    return {
        "total_enrolled": len(enrolled),
        "total_fee": total_fee,
        "enrollments": enrolled
    }

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:   
            return {"course": course}
    return {"error": "Course not found"}
