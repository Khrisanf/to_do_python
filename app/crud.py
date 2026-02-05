from sqlalchemy.orm import Session

from app import models, schemas


def create_user(db: Session, user_in: schemas.UserCreate, hashed_password: str, token: str) -> models.User:
    user = models.User(
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        token=token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_task(db: Session, task_in: schemas.TaskCreate) -> models.Task:
    task = models.Task(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def list_tasks(
    db: Session,
    status: models.TaskStatus | None = None,
    topic: str | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
) -> list[models.Task]:
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    if topic:
        query = query.filter(models.Task.topic == topic)
    if assignee_id:
        query = query.filter(models.Task.assignee_id == assignee_id)
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%"))
    return query.order_by(models.Task.created_at.desc()).all()


def update_task(db: Session, task: models.Task, task_in: schemas.TaskUpdate) -> models.Task:
    data = task_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    db.delete(task)
    db.commit()
