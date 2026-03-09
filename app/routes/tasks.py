from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_task = Task(
        title=task.title,
        assigned_to=task.assigned_to,
        created_by=current_user["id"],
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "admin":
        return db.query(Task).all()
    return db.query(Task).filter(Task.assigned_to == current_user["id"]).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user["role"] != "admin" and task.assigned_to != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return task


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, status_update: dict, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user["role"] != "admin" and task.assigned_to != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    new_status = status_update.get("status")
    if new_status not in ("pending", "in_progress", "done"):
        raise HTTPException(status_code=400, detail="Invalid status. Use: pending, in_progress, done")
    task.status = new_status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete tasks")
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
