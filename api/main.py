from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import time
from database import engine, get_db, Base
from models import TaskItem

# Ждем готовности PostgreSQL
print("Ожидание готовности базы данных...")
for i in range(10):
    try:
        Base.metadata.create_all(bind=engine)
        print("База данных готова!")
        break
    except Exception as e:
        print(f"Попытка {i+1}/10: БД еще не готова, ждем...")
        time.sleep(2)
else:
    print("Предупреждение: Не удалось подключиться к БД после 10 попыток")

app = FastAPI(title="Task API")

# Pydantic модели для валидации
class TaskCreate(BaseModel):
    title: str
    is_completed: bool = False

class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: bool

    class Config:
        from_attributes = True

# CREATE
@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskItem(title=task.title, is_completed=task.is_completed)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# READ (all)
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskItem).all()

# READ (one)
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskItem).filter(TaskItem.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# UPDATE
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(TaskItem).filter(TaskItem.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.title = task.title
    db_task.is_completed = task.is_completed
    db.commit()
    db.refresh(db_task)
    return db_task

# DELETE
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskItem).filter(TaskItem.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}