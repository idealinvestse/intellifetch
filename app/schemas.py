# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class CohabitantSchema(BaseModel):
    name: str = Field(..., example="Rickard Hedlund")
    age: Optional[str] = Field(None, example="35")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Rickard Hedlund",
                "age": "35"
            }
        }

class VehicleSchema(BaseModel):
    make_model: str = Field(..., example="BMW 320d Gran Turismo")
    model_year: Optional[str] = Field(None, example="2018")
    owner: Optional[str] = Field(None, example="Rickard Hedlund")
    registration: Optional[str] = Field(None, example="Volvo 745-883 GL")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "make_model": "BMW 320d Gran Turismo",
                "model_year": "2018",
                "owner": "Rickard Hedlund",
                "registration": "Volvo 745-883 GL"
            }
        }

class CompanyEngagementSchema(BaseModel):
    company_name: str = Field(..., example="Idealinvest Sverige AB")
    position: Optional[str] = Field(None, example="Styrelseledamot")
    company_url: Optional[str] = Field(None, example="https://www.merinfo.se/foretag/Idealinvest-Sverige-AB-5593040370/2khy9ki-23mci")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "company_name": "Idealinvest Sverige AB",
                "position": "Styrelseledamot",
                "company_url": "https://www.merinfo.se/foretag/Idealinvest-Sverige-AB-5593040370/2khy9ki-23mci"
            }
        }

class PersonInput(BaseModel):
    first_name: str = Field(..., example="Carl-Filip")
    last_name: str = Field(..., example="Grönlund")
    city: str = Field(..., example="Borlänge")

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Carl-Filip",
                "last_name": "Grönlund",
                "city": "Borlänge"
            }
        }

class PersonOutput(BaseModel):
    id: int = Field(..., example=1)
    full_name: str = Field(..., example="Carl-Filip Grönlund")
    age: Optional[str] = Field(None, example="32")
    city: Optional[str] = Field(None, example="Borlänge")
    address: Optional[str] = Field(None, example="Kalkstensgatan 1, 78445 Borlänge")
    phone_number: Optional[str] = Field(None, example="070-413 74 05")
    birthday: Optional[str] = Field(None, example="28:e juli (33 år)")
    national_id: Optional[str] = Field(None, example="19920728-1552")
    marital_status: Optional[str] = Field(None, example="ogift")
    cohabitants: List[CohabitantSchema] = Field(default_factory=list, example=[
        {
            "name": "Rickard Hedlund",
            "age": "35"
        }
    ])
    vehicles: List[VehicleSchema] = Field(default_factory=list, example=[
        {
            "make_model": "BMW 320d Gran Turismo",
            "model_year": "2018",
            "owner": "Rickard Hedlund",
            "registration": "Volvo 745-883 GL"
        }
    ])
    companies: List[CompanyEngagementSchema] = Field(default_factory=list, example=[
        {
            "company_name": "Idealinvest Sverige AB",
            "position": "Styrelseledamot",
            "company_url": "https://www.merinfo.se/foretag/Idealinvest-Sverige-AB-5593040370/2khy9ki-23mci"
        }
    ])

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "full_name": "Carl-Filip Grönlund",
                "age": "32",
                "city": "Borlänge",
                "address": "Kalkstensgatan 1, 78445 Borlänge",
                "phone_number": "070-413 74 05",
                "birthday": "28:e juli (33 år)",
                "national_id": "19920728-1552",
                "marital_status": "ogift",
                "cohabitants": [
                    {
                        "name": "Rickard Hedlund",
                        "age": "35"
                    }
                ],
                "vehicles": [
                    {
                        "make_model": "BMW 320d Gran Turismo",
                        "model_year": "2018",
                        "owner": "Rickard Hedlund",
                        "registration": "Volvo 745-883 GL"
                    }
                ],
                "companies": [
                    {
                        "company_name": "Idealinvest Sverige AB",
                        "position": "Styrelseledamot",
                        "company_url": "https://www.merinfo.se/foretag/Idealinvest-Sverige-AB-5593040370/2khy9ki-23mci"
                    }
                ]
            }
        }

class TaskStatus(BaseModel):
    task_id: str = Field(..., example="celery_task_id")
    message: str = Field(..., example="Scraping in progress. Use task ID to retrieve results.")
    
    class Config:
        schema_extra = {
            "example": {
                "task_id": "celery_task_id",
                "message": "Scraping in progress. Use task ID to retrieve results."
            }
        }