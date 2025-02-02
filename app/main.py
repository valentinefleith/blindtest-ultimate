from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import users, auth, playlists, deezer, songs, websockets
from app.services import rooms

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello Blindtest!"}


app.include_router(users.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(playlists.router, prefix="/api")
app.include_router(deezer.router, prefix="/api")
app.include_router(songs.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")
app.include_router(websockets.router)


Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À sécuriser en prod !
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
