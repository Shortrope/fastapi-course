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


def find_post_index(id):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return int(i)


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
    index = find_post_index(id)
    print("index: ", index)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    del my_posts[index]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post(id: int, post: Post):
    index = find_post_index(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
    post_dict = post.dict()
    # If the data in the body includes an 'id', it should match the url 'id'. If the id's
    # do not match, it could create two items with the same id!
    if post_dict.get("id") and post_dict.get("id") != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Url id ({id}) does not match the content id ('id': {post_dict['id']})",
        )
    post_dict = post.dict()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
