# Start server: uvicorn main:app --reload

import time

import psycopg2
from fastapi import FastAPI, status
from psycopg2.extras import RealDictCursor

from . import models
from .database import engine
from .routers import auth, posts, users

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
        "owner_id": 1,
    },
    {"title": "Favorite Foods", "content": "I like pizza", "owner_id": 2},
    {
        "title": "Rescue ToolKit",
        "content": "The ultimate linux recovery DVD",
        "owner_id": 3,
    },
]


@app.get("/")
def root():
    return {"message": "API Buddy: Using Postgres, Pscopg2 and SQLAlchemy"}


app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)


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
            """INSERT INTO posts (title, content, owner_id) VALUES (%s, %s, %s) RETURNING *;""",
            (post.get("title"), post["content"], post.get("owner_id")),
        )
        new_post = cursor.fetchone()
        conn.commit()

    return {"detail": "Database has been reset!"}
