from fastapi import FastAPI
from aircraft import routers as aircraft_routers

from user import routers as user_routers

app = FastAPI()

app.include_router(aircraft_routers.router)
app.include_router(user_routers.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
