# Start server: uvicorn main:app --reload

import time
from random import randrange
from typing import Optional

import psycopg2
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()

HOST = "localhost"
DB = "fastapi"
USER = "postgres"
PASSWORD = "postgres"

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


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


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
    return {"message": "API Buddy"}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts;""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;""",
        (post.title, post.content, post.published),
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s ;""", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    return {"post_detail": post}


@app.delete("/posts/{id}")
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (id,))
    deleted_post = cursor.fetchone()
    conn.commit()
    print(deleted_post)
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *;""",
        (
            post.title,
            post.content,
            post.published,
            id,
        ),
    )
    updated_post = cursor.fetchone()
    conn.commit()
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    return {"data": updated_post}


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
