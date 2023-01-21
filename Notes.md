# Notes
- `uvicorn main:app --reload`
- Pydantic: BaseModel
    - new_post.dict()   # returns a Pydantic BaseModel object as a dict
- MyPy - Typing a dict. Trouble with fastapi.params Body
- payload = Body(...) # expanding a dict. 
- from typing import Optional
- Postman
    - Body options: raw and json
- http://localhost:8000/docs

## Pydantic
- pydantic  BaseModel
- pydantic inheritance
- pydantic model for requests and responses

## DB
- psycopg2  postgresql driver/connector
- sqlalchemy    db orm





## SQL
### Create table
CREATE TABLE IF NOT EXISTS u_mak (
    id SERIAL PRIMARY KEY,
    email varchar UNIQUE NOT NULL,
    password varchar NOT NULL,
    created_on timestamptz NOT NULL DEFAULT now()
)

CREATE TABLE IF NOT EXISTS p_mak (
    id SERIAL PRIMARY KEY,
    title varchar NOT NULL,
    content text NOT NULL,
    published boolean NOT NULL DEFAULT TRUE,
    created_on timestamptz NOT NULL DEFAULT now()
)

ALTER TABLE p_mak
    ADD COLUMN u_id INT

ALTER TABLE p_mak
    ADD CONSTRAINT u_id_fk
        FOREIGN KEY(u_id) REFERENCES u_mak(id)
        ON DELETE SET NULL


### Add column