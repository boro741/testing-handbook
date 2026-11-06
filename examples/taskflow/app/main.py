"""TaskFlow: a small fictional task app used by every example in the handbook.

Simplified on purpose. Locally there is no SQS/SNS, no Redis and no ECS.
The production reference architecture is described in docs/start-here/taskflow-reference.
DEMO ONLY: passwords are stored in plain text. Never do this in a real app.
"""
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

PRIORITIES = {"LOW", "MEDIUM", "HIGH"}
# Allowed status moves. Anything else returns 409 Conflict.
TRANSITIONS = {
    "TODO": {"IN_PROGRESS"},
    "IN_PROGRESS": {"IN_REVIEW", "TODO"},
    "IN_REVIEW": {"DONE", "IN_PROGRESS"},
    "DONE": {"REOPENED"},
    "REOPENED": {"IN_PROGRESS"},
}
TOKENS: dict[str, int] = {}  # token -> user id (in memory; demo only)


def bug_on(bug_id: str) -> bool:
    """Practice switch for the handbook's bug hunt.

    True when the TASKFLOW_BUGS environment variable (comma list) names bug_id or 'all'.
    Unset or empty means the app behaves correctly. Read on every call, so tests can change it.
    """
    enabled = [b.strip() for b in os.environ.get("TASKFLOW_BUGS", "").split(",")]
    return bug_id in enabled or "all" in enabled


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class ProjectMember(Base):
    __tablename__ = "project_members"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), default="TODO")
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


def seed(session: Session) -> None:
    """Create demo users and one project. Safe to run more than once."""
    if session.scalar(select(User).limit(1)):
        return
    alice = User(username="alice", password="alice-pass")
    bob = User(username="bob", password="bob-pass")
    session.add_all([alice, bob])
    session.flush()
    demo = Project(name="Demo project")
    session.add(demo)
    session.flush()
    session.add_all([ProjectMember(project_id=demo.id, user_id=alice.id),
                     ProjectMember(project_id=demo.id, user_id=bob.id)])
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed(session)
    yield


app = FastAPI(title="TaskFlow API", version="1.0.0", lifespan=lifespan)


def get_db():
    with SessionLocal() as session:
        yield session


def current_user_id(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    user_id = TOKENS.get(authorization.removeprefix("Bearer ").strip())
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return user_id


class LoginIn(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    priority: str
    project_id: int

    @field_validator("title", mode="wrap")
    @classmethod
    def check_title(cls, v, handler):
        if bug_on("B01") and isinstance(v, str) and len(v) > 100:
            return v
        return handler(v)

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, v: str) -> str:
        if v not in PRIORITIES and not bug_on("B08"):
            raise ValueError("priority must be LOW, MEDIUM or HIGH")
        return v


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    priority: str | None = None
    status: str | None = None

    @field_validator("priority")
    @classmethod
    def valid_priority(cls, v: str | None) -> str | None:
        if v is not None and v not in PRIORITIES:
            raise ValueError("priority must be LOW, MEDIUM or HIGH")
        return v


class AssignIn(BaseModel):
    user_id: int


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    member_ids: list[int] = []


def task_out(t: Task) -> dict:
    return {"id": t.id, "title": t.title, "priority": t.priority, "status": t.status,
            "project_id": t.project_id, "assignee_id": t.assignee_id}


def require_member(db: Session, project_id: int, user_id: int) -> None:
    if db.get(ProjectMember, (project_id, user_id)) is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not a member of this project")


@app.post("/api/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == body.username))
    wrong_password = user is not None and user.password != body.password
    if bug_on("B06") and user is not None and user.username == "bob":
        wrong_password = False
    if user is None or wrong_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong username or password")
    token = uuid.uuid4().hex
    TOKENS[token] = user.id
    return {"token": token, "user_id": user.id}


@app.post("/api/projects", status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, me: int = Depends(current_user_id), db: Session = Depends(get_db)):
    project = Project(name=body.name)
    db.add(project)
    db.flush()
    for uid in set(body.member_ids) | {me}:
        db.add(ProjectMember(project_id=project.id, user_id=uid))
    db.commit()
    return {"id": project.id, "name": project.name}


@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate, me: int = Depends(current_user_id), db: Session = Depends(get_db)):
    if db.get(Project, body.project_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    require_member(db, body.project_id, me)
    task = Task(title=body.title, priority=body.priority, project_id=body.project_id, status="TODO")
    db.add(task)
    db.commit()
    return task_out(task)


def load_task(db: Session, task_id: int, me: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    require_member(db, task.project_id, me)
    return task


@app.get("/api/tasks/{task_id}")
def get_task(task_id: int, me: int = Depends(current_user_id), db: Session = Depends(get_db)):
    if bug_on("B03"):
        task = db.get(Task, task_id)
        if task is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
        return task_out(task)
    return task_out(load_task(db, task_id, me))


@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate, me: int = Depends(current_user_id), db: Session = Depends(get_db)):
    task = load_task(db, task_id, me)
    if body.title is not None:
        task.title = body.title
    if body.priority is not None:
        task.priority = body.priority
    if body.status is not None and body.status != task.status:
        allowed = TRANSITIONS.get(task.status, set())
        if bug_on("B02") and task.status == "TODO":
            allowed = allowed | {"DONE"}
        if body.status not in allowed:
            raise HTTPException(status.HTTP_409_CONFLICT,
                                f"Cannot move from {task.status} to {body.status}")
        task.status = body.status
    db.commit()
    return task_out(task)


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, me: int = Depends(current_user_id), db: Session = Depends(get_db)):
    task = load_task(db, task_id, me)
    if bug_on("B05"):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/api/tasks/{task_id}/assign")
def assign_task(task_id: int, body: AssignIn, me: int = Depends(current_user_id), db: Session = Depends(get_db)):
    task = load_task(db, task_id, me)
    if db.get(ProjectMember, (task.project_id, body.user_id)) is None and not bug_on("B04"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Assignee is not a project member")
    task.assignee_id = body.user_id
    db.commit()
    return task_out(task)


@app.get("/api/tasks")
def list_tasks(project_id: int, me: int = Depends(current_user_id), db: Session = Depends(get_db)):
    require_member(db, project_id, me)
    query = select(Task)
    if not bug_on("B07"):
        query = query.where(Task.project_id == project_id)
    rows = db.scalars(query.order_by(Task.id)).all()
    return [task_out(t) for t in rows]


@app.get("/health")
def health():
    return {"status": "ok"}


STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def ui():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
