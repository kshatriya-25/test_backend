from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, tasks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users")
app.include_router(tasks.router, prefix="/tasks")
