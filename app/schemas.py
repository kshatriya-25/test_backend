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