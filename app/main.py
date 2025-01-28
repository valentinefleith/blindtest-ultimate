from fastapi import FastAPI
from app.database import Base, engine
from app.routes import users

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello Blindtest!"}


app.include_router(users.router, prefix="/api")

Base.metadata.create_all(bind=engine)
