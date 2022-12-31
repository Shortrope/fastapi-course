# Start server: uvicorn main:app --reload

from random import randrange
from typing import Optional

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI()


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


def find_post(id: int):
    for post in my_posts:
        if post["id"] == id:
            return post
    # return {"error": f"id: {id} not found!"}


def find_post_index(id):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return int(i)


@app.get("/")
def root():
    return {"message": "API Buddy"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"id: {id} not found!"
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"id: {id} not found!"}
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
