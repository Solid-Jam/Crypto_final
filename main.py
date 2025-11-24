from fastapi import FastAPI
from routers import users, api_key, assets, assets
from database import create_database

app = FastAPI(
    title="Crypto Tracker",
    description="A Crypto Tracker for managing cryptocurrency data",
    version="1.0.0"
)

app.include_router(users.router, prefix='/api/users', tags=["Users"])
app.include_router(assets.router, prefix='/api/assets', tags=["Assets"])
app.include_router(api_key.router, prefix='/api/validate_key')

@app.on_event('startup')
def startup():
    create_database()