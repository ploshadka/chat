import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import history, users, groups, login
from app.websockets import chat as chat_ws
from app.routers import chat as chat_api

app = FastAPI()

env = os.getenv("ENV", "dev")

# Условия для CORS
if env == "dev":
    origins = ["http://localhost:5173"]
else:
    origins = ["https://yourdomain.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # если используется авторизация или куки
    allow_methods=["*"],
    allow_headers=["*"],
)

# API
app.include_router(login.router)
app.include_router(history.router)
app.include_router(chat_api.router)
app.include_router(groups.router)
app.include_router(users.router)

# WebSocket
app.include_router(chat_ws.router)
