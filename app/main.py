from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app import analytics, crud, models, schemas
from app.auth import create_token, get_current_user, hash_password, verify_password
from app.db import Base, get_db, get_engine

app = FastAPI(title="Task Tracker")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=get_engine())


@app.post("/auth/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserOut:
    existing = crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username exists")
    token = create_token()
    user = crud.create_user(db, user_in, hash_password(user_in.password), token)
    return user


@app.post("/auth/login", response_model=schemas.TokenOut)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)) -> schemas.TokenOut:
    user = crud.get_user_by_username(db, user_in.username)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_token()
    user = crud.update_user_token(db, user, token)
    return schemas.TokenOut(token=user.token)


@app.post("/tasks", response_model=schemas.TaskOut)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> schemas.TaskOut:
    if task_in.assignee_id:
        assignee = crud.get_user_by_id(db, task_in.assignee_id)
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
    return crud.create_task(db, task_in)


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    status: models.TaskStatus | None = None,
    topic: str | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> list[schemas.TaskOut]:
    return crud.list_tasks(db, status=status, topic=topic, assignee_id=assignee_id, search=search)


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> schemas.TaskOut:
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> schemas.TaskOut:
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task_in.assignee_id:
        assignee = crud.get_user_by_id(db, task_in.assignee_id)
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
    return crud.update_task(db, task, task_in)


@app.patch("/tasks/{task_id}/status", response_model=schemas.TaskOut)
def update_status(
    task_id: int,
    status_in: models.TaskStatus,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> schemas.TaskOut:
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return crud.update_task(db, task, schemas.TaskUpdate(status=status_in))


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> None:
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    crud.delete_task(db, task)


@app.get("/tasks/analytics", response_model=schemas.AnalyticsResponse)
def task_analytics(
    group_by: str = "status",
    with_chart: bool = False,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
) -> schemas.AnalyticsResponse:
    if group_by not in analytics.GROUP_FIELDS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid group_by")
    df = analytics.build_task_dataframe(db)
    grouped = analytics.compute_group_stats(df, group_by)
    chart = analytics.build_chart(grouped, group_by) if with_chart else None
    return schemas.AnalyticsResponse(
        group_by=group_by,
        total=len(df.index),
        data=[schemas.AnalyticsGroup(label=str(row[group_by]), count=row["count"]) for row in grouped],
        chart_base64=chart,
    )
