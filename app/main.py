# app/main.py
from fastapi import FastAPI, HTTPException
from .schemas import PersonInput, PersonOutput
from .tasks import scrape_and_store
from .config import logger
import os
from .database import SessionLocal, Base, engine
from fastapi.middleware.cors import CORSMiddleware

# Skapa databastabellerna vid start
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Merinfo Scraper API",
    description="API för att skrapa personuppgifter från Merinfo.se och lagra dem i en databas.",
    version="1.0.0"
)

# Konfigurera CORS om det behövs
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Lägg till fler ursprung om det behövs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scrape-person/", response_model=PersonOutput)
def scrape_person(person: PersonInput):
    logger.info(f"Received request to scrape person: {person.first_name} {person.last_name} in {person.city}")
    task = scrape_and_store.delay(person.first_name, person.last_name, person.city)
    logger.info(f"Task {task.id} started for scraping.")
    return {"id": task.id, "message": "Scraping in progress. Use task ID to retrieve results."}

@app.get("/task-result/{task_id}", response_model=PersonOutput)
def get_task_result(task_id: str):
    from celery.result import AsyncResult
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        # Jobben har inte körts ännu
        raise HTTPException(status_code=202, detail="Task is still processing.")
    elif task.state == 'FAILURE':
        # Tasken misslyckades
        raise HTTPException(status_code=500, detail=str(task.info))
    elif task.state == 'SUCCESS':
        return task.result
    else:
        raise HTTPException(status_code=400, detail="Unknown task state.")