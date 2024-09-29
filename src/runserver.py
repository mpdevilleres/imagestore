from fastapi import FastAPI
from src.factory import create_app

app: FastAPI = create_app()
