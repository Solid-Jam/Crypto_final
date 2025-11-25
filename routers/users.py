import sqlite3
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from models.user import User, UserCreate
from database import get_db_connection
from auth.security import get_api_key

router = APIRouter()


@router.get('/', response_model=List[User])
def get_users(_: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    conn.close()

    return [{"id": u["id"], "username": u["username"]} for u in users]


@router.post('/', response_model=User)
def create_user(user: UserCreate):   # <-- API KEY REMOVED HERE
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user.username, user.password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return User(id=user_id, username=user.username)

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User '{user.username}' already exists."
        )

    finally:
        conn.close()


@router.put('/{user_id}', response_model=User)
def update_user(user_id: int, user: UserCreate, _: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET username = ?, password = ? WHERE id = ?",
        (user.username, user.password, user_id)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    conn.commit()
    conn.close()
    return User(id=user_id, username=user.username)


@router.delete('/{user_id}', response_model=dict)
def delete_user(user_id: int, _: str = Depends(get_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    conn.commit()
    conn.close()

    return {"detail": "User deleted"}
