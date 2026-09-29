from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import create_db_and_tables
from models.schemas import HealthResponse
from routes import agent, auth

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth.router, prefix="/auth")
app.include_router(agent.router)


@app.get("/")
def index():
    return RedirectResponse(url="/static/index.html")


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok")
