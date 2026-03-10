from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.routes import users, tasks
from app.database import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users")
app.include_router(tasks.router, prefix="/tasks")

@app.get("/health")
def health_check():
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    status = "ok" if db_status == "ok" else "degraded"
    return JSONResponse(
        status_code=200 if status == "ok" else 503,
        content={"status": status, "server": "ok", "database": db_status},
    )
