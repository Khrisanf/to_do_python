from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import TaskStatus


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    token: str
    token_type: str = "bearer"


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.new
    topic: Optional[str] = Field(default=None, max_length=100)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.new
    topic: Optional[str] = Field(default=None, max_length=100)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    topic: Optional[str] = Field(default=None, max_length=100)


class TaskOut(TaskBase):
    id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalyticsGroup(BaseModel):
    label: str
    count: int


class AnalyticsResponse(BaseModel):
    group_by: str
    total: int
    data: list[AnalyticsGroup]
    chart_base64: Optional[str] = None
