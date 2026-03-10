from pydantic import BaseModel, field_validator

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

    @field_validator("assigned_to")
    @classmethod
    def assigned_to_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("assigned_to must be a positive integer")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    status: str
    assigned_to: int

    class Config:
        from_attributes = True