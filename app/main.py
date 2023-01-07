# Start server: uvicorn main:app --reload
import time
from random import randrange
from typing import Optional

import psycopg2
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.params import Body
from psycopg2.extras import RealDictCursor
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


HOST = "localhost"
DB = "fastapi"
USER = "fastapi"
PASSWORD = "fastapi"

# Give psycopg 3 seconds to connect
for i in range(3):
    try:
        conn = psycopg2.connect(
            host=HOST,
            database=DB,
            user=USER,
            password=PASSWORD,
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print(f"Successful connection to '{DB}' database")
        break
    except Exception as error:
        print(f"Connection to '{DB}' database failed! Try {i+1} of 3")
        print("Error: ", error)
        time.sleep(1)


my_posts = [
    {
        "title": "Top beaches in Florida",
        "content": "Check out these awesome beaches",
        "id": 1,
    },
    {
        "title": "Favorite Foods",
        "content": "I like pizza",
        "id": 2,
    },
]


@app.get("/")
def root():
    return {"message": "API Buddy: Using Postgres, Pscopg2 and SQLAlchemy"}


@app.get("/posts", response_model=list[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    return post


@app.post(
    "/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published
    # )
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.delete("/posts/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put(
    "/posts/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PostResponse,
)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    print(post_query)
    original_post = post_query.first()
    if not original_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@app.get("/resetdb", status_code=status.HTTP_201_CREATED)
def reset_db():
    print("*** RESET DB ***")
    print("Deleting posts...")
    cursor.execute("""SELECT * FROM posts;""")
    all_posts = cursor.fetchall()
    for post in all_posts:
        print("Deleting: ", post)
        id = post.get("id")
        cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (id,))
        deleted_post = cursor.fetchone()
        conn.commit()
        print(deleted_post)

    print("Adding default posts to db...")
    for post in my_posts:
        print("Adding: ", post)
        cursor.execute(
            """INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *;""",
            (post.get("title"), post["content"]),
        )
        new_post = cursor.fetchone()
        conn.commit()

    return {"detail": "Database has been reset!"}


@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/users/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Id {id} not found"
        )

    return user


@app.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # check if email already used
    email_query = db.query(models.User).filter(models.User.email == user.email)
    if email_query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict: {user.email} already exists!",
        )

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.put("/users/{id}", status_code=status.HTTP_201_CREATED)
def update_user(id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user_found_in_db = user_query.first()

    # check if user exists
    if not user_found_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{id} not found!",
        )

    # if email address changed, is it already registered
    if user_found_in_db.email != user.email:
        is_other_user_with_email = (
            db.query(models.User).filter(models.User.email == user.email).first()
        )
        if is_other_user_with_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"UniqueViolation: {user.email} is registered to another user!",
            )

    user_query.update(user.dict(), synchronize_session=False)
    db.commit()

    return user_query.first()
    # return {"detail": "Testing"}


@app.delete("/users/{id}")
def delete_user(id: int):
    return {"detail": "Delete User"}
