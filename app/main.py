from fastapi import FastAPI
from .routers import voyage, driver, passenger
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


app.include_router(voyage.router)
app.include_router(driver.router)
app.include_router(passenger.router)


@app.get("/")
async def root():
    return {"Hello": "World"}
