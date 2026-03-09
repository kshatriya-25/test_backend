# FastAPI Task Manager Backend

This project demonstrates a minimal backend for a **Task Manager application** using:

* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic (database migrations)
* JWT Authentication
* Pydantic validation

It is designed as a **teaching project for understanding full stack development**.

---

# 1. Prerequisites

Make sure you have installed:

* Python 3.10+
* PostgreSQL
* Git

Check versions:

```bash
python --version
psql --version
git --version
```

---

# 2. Project Structure

```
backend
│
├── app
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── routes
│       ├── users.py
│       └── tasks.py
│
├── alembic
│   └── versions
│
├── alembic.ini
├── requirements.txt
├── .env
└── README.md
```

---

# 3. Create Virtual Environment

Create virtual environment:

```bash
python -m venv venv
```

Activate it.

### Mac / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

# 4. Create `requirements.txt`

Create a file named `requirements.txt`:

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
alembic
pydantic
pydantic-settings
python-jose
passlib[bcrypt]
bcrypt==4.0.1
python-multipart
python-dotenv
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 5. Setup Environment Variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/taskmanager

JWT_SECRET=supersecretkey
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

# 6. PostgreSQL Setup

Login to PostgreSQL:

```bash
psql -U postgres
```

Create the database:

```sql
CREATE DATABASE taskmanager;
```

Verify:

```sql
\l
```

Exit:

```sql
\q
```

---

# 7. Database Configuration

Create `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

# 8. Configuration using Pydantic

Create `app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()
```

---

# 9. Initialize Alembic

Run:

```bash
alembic init alembic
```

This creates:

```
alembic/
alembic.ini
```

---

# 10. Configure Alembic

Open:

```
alembic/env.py
```

Add imports:

```python
from app.config import settings
from app.database import Base
from app import models
```

Find:

```python
config = context.config
```

Add:

```python
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

Replace:

```python
target_metadata = None
```

With:

```python
target_metadata = Base.metadata
```

---

# 11. Create Database Models

Create `app/models.py`

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="pending")
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

# 12. Create Pydantic Schemas

Create `app/schemas.py`

```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str


class UserLogin(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str
    assigned_to: int


class TaskResponse(BaseModel):
    id: int
    title: str
    status: str
    assigned_to: int

    class Config:
        from_attributes = True
```

---

# 13. Generate Migration

Run:

```bash
alembic revision --autogenerate -m "create users and tasks tables"
```

This creates a migration inside:

```
alembic/versions/
```

---

# 14. Apply Migration

Run:

```bash
alembic upgrade head
```

Verify tables in PostgreSQL:

```sql
\dt
```

Expected tables:

```
users
tasks
alembic_version
```

---

# 15. Authentication Utilities

Create `app/auth.py`

```python
from jose import jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

def create_token(data: dict):
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

---

# 16. User Routes

Create `app/routes/users.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserCreate
from app.auth import hash_pswd, verify_pswd, create_access_token, get_current_user

router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = User(
        username=user.username,
        password_hash=hash_pswd(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "role": new_user.role}


@router.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_pswd(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(db_user.id), "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}
```

---

# 17. Task Routes

Create `app/routes/tasks.py`

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/tasks")
def create_task():
    return {"message": "Task created"}

@router.get("/tasks")
def get_tasks():
    return []
```

---

# 18. FastAPI Application

Create `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users")
# app.include_router(tasks.router, prefix="/tasks")
```

---

# 19. Run FastAPI Server

Start server:

```bash
uvicorn app.main:app --reload
```

Open API documentation:

```
http://localhost:8000/docs
```

---

# 20. Authentication Flow

The application uses **JWT authentication**.

```
Register User
     ↓
Login
     ↓
Server generates JWT
     ↓
Client sends token in Authorization header
```

Header example:

```
Authorization: Bearer <token>
```

---

# 21. API Endpoints

## Register User

```
POST /users/register
```

Example request:

```json
{
  "username": "ankit",
  "password": "1234",
  "role": "admin"
}
```

---

## Login

```
POST /users/login
```

Example request:

```json
{
  "username": "ankit",
  "password": "1234"
}
```

Example response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

---

## Create Task

```
POST /tasks
```

---

## Get Tasks

```
GET /tasks
```

Returns all tasks.

---

# 22. Development Workflow

Typical workflow when modifying database models:

1. Modify `models.py`
2. Generate migration
3. Apply migration

Commands:

```bash
alembic revision --autogenerate -m "update schema"
alembic upgrade head
```

---

# 23. Running the Full Stack App

Start backend:

```bash
uvicorn app.main:app --reload
```

Start frontend (React):

```bash
npm run dev
```

Architecture flow:

```
React Frontend
      ↓
FastAPI Backend
      ↓
PostgreSQL Database
```

---

# 24. Learning Goals

This project demonstrates:

* Full stack architecture
* REST API development
* Authentication using JWT
* Database migrations with Alembic
* Frontend-backend communication
* Environment configuration using `.env`
* Clean backend project structure

---

**End of Guide**
