"""
Простое Todo-приложение на FastAPI + PostgreSQL.
Никакого Docker — запускается голыми руками на Linux.
"""

import os
from typing import List

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Todo API")

# Разрешаем фронтенду (открытому напрямую как файл или с другого порта) стучаться к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Настройки подключения к БД ---
# Берём из переменных окружения, чтобы не хардкодить пароль в коде.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tododb")
DB_USER = os.getenv("DB_USER", "todouser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "todopass")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )


def init_db():
    """Создаёт таблицу, если её ещё нет. Вызывается при старте приложения."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


class TodoCreate(BaseModel):
    title: str


class Todo(BaseModel):
    id: int
    title: str
    done: bool


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    """Проверка, что бэкенд жив и видит базу — пригодится для диагностики сетей."""
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {e}")


@app.get("/api/todos", response_model=List[Todo])
def list_todos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, done FROM todos ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.post("/api/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos (title, done) VALUES (%s, FALSE) RETURNING id, title, done",
        (todo.title,),
    )
    new_todo = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_todo


@app.put("/api/todos/{todo_id}/toggle", response_model=Todo)
def toggle_todo(todo_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE todos SET done = NOT done WHERE id = %s RETURNING id, title, done",
        (todo_id,),
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"deleted": todo_id}
