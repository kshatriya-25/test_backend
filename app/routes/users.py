from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
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


@router.get("/")
async def get_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users]


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "role": user.role}


@router.put("/{user_id}")
async def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.password_hash = hash_pswd(user.password)
    db_user.role = user.role
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "role": db_user.role}


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
