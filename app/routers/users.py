from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import get_db

router = APIRouter()


@router.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/users/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Id {id} not found"
        )

    return user


@router.post(
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

    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.put(
    "/users/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse,
)
def update_user(id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user_found_in_db = user_query.first()

    # check if user exists
    if not user_found_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{id} not found!",
        )

    # if email address changed, is it already registered to another user
    if user_found_in_db.email != user.email:
        is_other_user_with_email = (
            db.query(models.User).filter(models.User.email == user.email).first()
        )
        if is_other_user_with_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"UniqueViolation: {user.email} is registered to another user!",
            )

    # checks passed... update the db
    user.password = utils.hash(user.password)
    user_query.update(user.dict(), synchronize_session=False)
    db.commit()

    return user_query.first()


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Id {id} not found!"
        )

    user_query.delete(synchronize_session=False)
    db.commit()
    return {"detail": f"Deleted user with id: {id}"}
