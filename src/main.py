from fastapi import FastAPI
from contextlib import asynccontextmanager
from mangum import Mangum

from .utils import Utils


@asynccontextmanager
async def app_lifespan(application: FastAPI):
    Utils.log_info("Starting the application")
    yield


app = FastAPI(
    title="ChatBot API",
    description="Chatbot API description",
    version="1.0.0",
    lifespan=app_lifespan,
)


@app.get("/")
async def root():
    return {"msg": "Hello World"}


handler = Mangum(app)
