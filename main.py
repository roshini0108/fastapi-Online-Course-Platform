from unicodedata import category
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import HTTPException
from fastapi import Query
import math 

app = FastAPI()
# In-memory data storage
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
#Q6 - Pydantic model for enroll request with validations and default values
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

#Q7 - Helper function to find course by ID
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

# Q1 — Home route
@app.get("/")
def home():
    return {"message": "Welcome to LearnHub Online Courses"}

# Q2 — Get all courses
@app.get("/courses")
def get_courses():
    return {"courses": courses}

# Q4 — Get all enrollments
@app.get("/enrollments")
def get_enrollments():
    return {"enrollments": enrollments, "total": len(enrollments)}

# Q5 — Course summary
@app.get("/courses/summary")
def get_course_summary():
    return {
  "total_courses": len(courses),
  "free_courses": len([course for course in courses if course["price"] == 0]),
  "most_expensive_course": max(courses, key=lambda x: x["price"]) if courses else None,
  "total_seats": sum(course["seats_left"] for course in courses),
  "category_count": {category: len([course for course in courses if course["category"] == category]) for category in set(course["category"] for course in courses)}
}

# Q6 — Test enroll endpoint
@app.post("/test-enroll")
def test_enroll(data: EnrollRequest):
    return {"message": "ok"}

#Q8 - Enroll  in a course with validations, discount , seat update
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
    #Q9- Include gift enrollment details in the record
    "gift_enrollment": data.gift_enrollment,
    "recipient_name": data.recipient_name if data.gift_enrollment else None
    }
    enrollments.append(record)
    enrollment_counter += 1 
    return {"message": "Enrollment successful", "enrollment": record}

#Q10 - Filter courses by category, level, price and seat availability
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

#Q11 - Add new course with validation and duplicate title check
@app.post("/courses", status_code=201)
def add_course(course: NewCourse):
    for c in courses:
        if c["title"].lower() == course.title.lower():
            raise HTTPException(status_code=400, detail="Course with this title already exists")
    new_course = course.dict()
    new_course["id"] = max(c["id"] for c in courses) + 1 if courses else 1
    courses.append(new_course)
    return {"message": "Course added successfully", "course": new_course}

#Q14 - Wishlist management with add, view, enroll and remove functionality
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

#Q15 - Enroll in all wishlist courses with validations and fee calculation
@app.post("/wishlist/enroll-all")
def enroll_all(data: WishlistEnrollRequest):
    global enrollment_counter
    global wishlist
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
    
    wishlist = [item for item in wishlist if item["student_name"] != data.student_name]
    return {
        "total_enrolled": len(enrolled),
        "total_fee": total_fee,
        "enrollments": enrolled
    }

#Q16 - Search courses by keyword in title, instructor or category
@app.get("/courses/search")
def search_courses(keyword: str = Query(...)):
    keyword = keyword.lower()
    results = []
    for course in courses:
        if (
            keyword in course["title"].lower() or
            keyword in course["instructor"].lower() or
            keyword in course["category"].lower()
        ):
            results.append(course)
    return {
        "results": results,
        "total_found": len(results)
    }

#Q17 - Sort courses by price, title or seats left with ascending or descending order
@app.get("/courses/sort")
def sort_courses(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):
    valid_fields = ["price", "title", "seats_left"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")
    reverse = True if order == "desc" else False
    sorted_courses = sorted(courses, key=lambda x: x[sort_by], reverse=reverse)
    return {
        "sorted_courses": sorted_courses,
        "sort_by": sort_by,
        "order": order
    }

#Q18 - Paginate courses and enrollments with page number and limit
@app.get("/courses/page")
def paginate_courses(
    page: int = Query(1, gt=0),
    limit: int = Query(3, gt=0)
):
    total_courses = len(courses)
    total_pages = math.ceil(total_courses / limit)
    start = (page - 1) * limit
    end = start + limit
    paginated = courses[start:end]
    return {
        "current_page": page,
        "total_pages": total_pages,
        "total_courses": total_courses,
        "courses": paginated
    }

#Q19 - Search enrollments by student name with case-insensitive matching
@app.get("/enrollments/search")
def search_enrollments(keyword: str):
    keyword = keyword.lower()
    results = [
        e for e in enrollments
        if keyword in e["student_name"].lower()
    ]
    return {
        "results": results,
        "total_found": len(results)
    }
#Q19 - Sort enrollments by final fee with ascending or descending order
@app.get("/enrollments/sort")
def sort_enrollments(order: str = "asc"):
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")
    reverse = True if order == "desc" else False
    sorted_data = sorted(enrollments, key=lambda x: x["final_fee"], reverse=reverse)
    return {
        "sorted_enrollments": sorted_data,
        "order": order
    }
#Q19 - Paginate enrollments with page number and limit
@app.get("/enrollments/page")
def paginate_enrollments(page: int = 1, limit: int = 3):
    total = len(enrollments)
    total_pages = math.ceil(total / limit)
    start = (page - 1) * limit
    end = start + limit
    data = enrollments[start:end]
    return {
        "current_page": page,
        "total_pages": total_pages,
        "total_enrollments": total,
        "enrollments": data
    }

#Q20 - Combine filtering, sorting and pagination for courses in a single endpoint
@app.get("/courses/browse")
def browse_courses(
    keyword: str = Query(None),
    category: str = Query(None),
    level: str = Query(None),
    max_price: int = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, gt=0),
    limit: int = Query(3, gt=0)
):
    result = courses
    if keyword is not None:
        keyword = keyword.lower()
        result = [
            c for c in result
            if keyword in c["title"].lower()
            or keyword in c["instructor"].lower()
            or keyword in c["category"].lower()
        ]   
    if category is not None:
        result = [c for c in result if c["category"].lower() == category.lower()]
    if level is not None:
        result = [c for c in result if c["level"].lower() == level.lower()]
    if max_price is not None:
        result = [c for c in result if c["price"] <= max_price]
    valid_fields = ["price", "title", "seats_left"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")
    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)
    total = len(result)
    total_pages = math.ceil(total / limit)
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]
    return {
        "total_results": total,
        "total_pages": total_pages,
        "current_page": page,
        "courses": paginated
    }

#Q12 - Update course details with partial updates allowed
@app.put("/courses/{course_id}")
def update_course(
    course_id: int,
    price: int = Query(None),
    seats_left: int = Query(None)
):
    for c in courses:
        if c["id"] == course_id:
            if price is not None:
                c["price"] = price
            if seats_left is not None:
                c["seats_left"] = seats_left
            return {
                "message": "Course updated successfully",
                "course": c
            }
    raise HTTPException(status_code=404, detail="Course not found")

#Q13 - Delete a course with enrollment check
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

#Q15- delete a course from wishlist after enrolling in it
@app.delete("/wishlist/remove/{course_id}")
def remove_from_wishlist(course_id: int, student_name: str):
    for item in wishlist:
        if item["course_id"] == course_id and item["student_name"] == student_name:
            wishlist.remove(item)
            return {"message": "Course removed from wishlist"}
    raise HTTPException(status_code=404, detail="Item not found in wishlist")

#Q3 - Get course details by ID with error handling
@app.get("/courses/{course_id}")
def get_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:   
            return {"course": course}
    return {"error": "Course not found"}
