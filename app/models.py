from sqlalchemy import Column , Integer , String , ForeignKey , DateTime
from sqlalchemy import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer , primary_key=True , index=True)
    username = Column(String , unique=True , nullable=False)
    password_hash = Column(String , nullable=False)
    role = Column(String , nullable=False)
    created_at = Column(DateTime(timezone=True) , server_default=func.now())
    tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    status = Column(String, default="pending")

    assigned_to = Column(Integer, ForeignKey("users.id"))

    created_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())