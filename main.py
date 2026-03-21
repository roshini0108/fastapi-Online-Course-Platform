from fastapi import FastAPI
app = FastAPI()
courses=[
    {"id":1,"title":"Full Stack Web Development","instructor":"John Doe","category":"Web Dev","level":"Beginner","price":99,"seats_left":20},
    {"id":2,"title":"Backend APIs with FastAPI","instructor":"Jane Smith","category":"Web Dev","level":"Advanced","price":299,"seats_left":15},
    {"id":3,"title":"Machine Learning Fundamentals","instructor":"Bob Johnson","category":"Data Science","level":"Intermediate","price":199,"seats_left":10},
    {"id":4,"title":"Figma for Beginners","instructor":"Alice Williams","category":"Design","level":"Intermediate","price":199,"seats_left":5},
    {"id":5,"title":"Docker & Kubernetes Basics","instructor":"Charlie Brown","category":"DevOps","level":"Beginner","price":99,"seats_left":25},
    {"id":6,"title":"Linux for DevOps Engineers","instructor":"David Davis","category":"DevOps","level":"Advanced","price":299,"seats_left":20}
]
@app.get("/")
def home():
    return {"message": "Welcome to LearnHub Online Courses"}

@app.get("/courses")
def get_courses():
    return {"courses": courses, "total": len(courses), "total_seats_available": sum(course["seats_left"] for course in courses)}
