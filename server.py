from fastapi import FastAPI
import uvicorn
from client import get_latest_schedule


app = FastAPI()


@app.post("/api/sc/week")
async def get_weekly_schedule():
    return await get_latest_schedule()