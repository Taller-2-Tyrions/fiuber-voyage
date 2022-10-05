from fastapi import FastAPI
from .routers import pricing, voyage
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(pricing.router)
app.include_router(voyage.router)


@app.get("/")
async def root():
    return {"Hello": "World"}
