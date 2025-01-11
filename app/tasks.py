# app/tasks.py
from celery import Celery
import os
from .scraper import scrape_merinfo
from .database import SessionLocal, Base, engine
from .models import Person, Cohabitant, Vehicle, CompanyEngagement
from .schemas import PersonOutput
from sqlalchemy.orm import Session
from .config import logger
from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task(bind=True, max_retries=3)
def scrape_and_store(self, first_name: str, last_name: str, city: str):
    try:
        logger.info(f"Starting scrape task for {first_name} {last_name} in {city}")
        data = scrape_merinfo(first_name, last_name, city)
        if not data or not data.get('full_name'):
            raise ValueError("Person not found or scraping failed.")
        
        db: Session = SessionLocal()
        try:
            # Kontrollera om personen redan finns
            existing_person = db.query(Person).filter(Person.full_name == data.get('full_name')).first()
            if existing_person:
                logger.warning(f"Person {data.get('full_name')} already exists in the database.")
                return {
                    "id": existing_person.id,
                    "full_name": existing_person.full_name,
                    "age": existing_person.age,
                    "city": existing_person.city,
                    "address": existing_person.address,
                    "phone_number": existing_person.phone_number,
                    "birthday": existing_person.birthday,
                    "national_id": existing_person.national_id,
                    "marital_status": existing_person.marital_status,
                    "cohabitants": [{"name": co.name, "age": co.age} for co in existing_person.cohabitants],
                    "vehicles": [{"make_model": veh.make_model, "model_year": veh.model_year, "owner": veh.owner, "registration": veh.registration} for veh in existing_person.vehicles],
                    "companies": [{"company_name": comp.company_name, "position": comp.position, "company_url": comp.company_url} for comp in existing_person.companies]
                }
        
            # Skapa ny person
            new_person = Person(
                full_name=data.get('full_name'),
                age=data.get('age'),
                city=data.get('city'),
                address=data.get('address'),
                phone_number=data.get('phone_number'),
                birthday=data.get('birthday'),
                national_id=data.get('national_id'),
                marital_status=data.get('marital_status')
            )
            db.add(new_person)
            db.commit()
            db.refresh(new_person)
            logger.info(f"Added new person: {new_person.full_name} with ID {new_person.id}")
            
            # Lägg till cohabitants
            for co in data.get('cohabitants', []):
                cohabit = Cohabitant(
                    name=co['name'],
                    age=co['age'],
                    person_id=new_person.id
                )
                db.add(cohabit)
            db.commit()
            logger.info(f"Added {len(data.get('cohabitants', []))} cohabitants.")
            
            # Lägg till vehicles
            for veh in data.get('vehicles', []):
                vehicle = Vehicle(
                    make_model=veh['make_model'],
                    model_year=veh['model_year'],
                    owner=veh['owner'],
                    registration=veh['registration'],
                    person_id=new_person.id
                )
                db.add(vehicle)
            db.commit()
            logger.info(f"Added {len(data.get('vehicles', []))} vehicles.")
            
            # Lägg till company engagements
            for comp in data.get('companies', []):
                company = CompanyEngagement(
                    company_name=comp['company_name'],
                    position=comp['position'],
                    company_url=comp['company_url'],
                    person_id=new_person.id
                )
                db.add(company)
            db.commit()
            logger.info(f"Added {len(data.get('companies', []))} company engagements.")
            
            # Förbered output
            output = {
                "id": new_person.id,
                "full_name": new_person.full_name,
                "age": new_person.age,
                "city": new_person.city,
                "address": new_person.address,
                "phone_number": new_person.phone_number,
                "birthday": new_person.birthday,
                "national_id": new_person.national_id,
                "marital_status": new_person.marital_status,
                "cohabitants": [{"name": co.name, "age": co.age} for co in new_person.cohabitants],
                "vehicles": [{"make_model": veh.make_model, "model_year": veh.model_year, "owner": veh.owner, "registration": veh.registration} for veh in new_person.vehicles],
                "companies": [{"company_name": comp.company_name, "position": comp.position, "company_url": comp.company_url} for comp in new_person.companies]
            }
            
            logger.info(f"Scraping and storing completed for {new_person.full_name}")
            return output

        except Exception as e:
            db.rollback()
            logger.error(f"Database error: {e}")
            raise self.retry(exc=e, countdown=60)
        finally:
            db.close()
    ```
    
#### `celery_worker.py`

```python
# celery_worker.py
from app.tasks import celery_app

if __name__ == '__main__':
    celery_app.start()