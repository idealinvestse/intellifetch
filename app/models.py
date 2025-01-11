# app/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, unique=True, index=True, nullable=False)
    age = Column(String)
    city = Column(String)
    address = Column(Text)
    phone_number = Column(String)
    birthday = Column(String)
    national_id = Column(String)
    marital_status = Column(String)
    cohabitants = relationship("Cohabitant", back_populates="person", cascade="all, delete")
    vehicles = relationship("Vehicle", back_populates="person", cascade="all, delete")
    companies = relationship("CompanyEngagement", back_populates="person", cascade="all, delete")

class Cohabitant(Base):
    __tablename__ = "cohabitants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(String)
    person_id = Column(Integer, ForeignKey('persons.id'))
    person = relationship("Person", back_populates="cohabitants")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    make_model = Column(String, nullable=False)
    model_year = Column(String)
    owner = Column(String)
    registration = Column(String)
    person_id = Column(Integer, ForeignKey('persons.id'))
    person = relationship("Person", back_populates="vehicles")

class CompanyEngagement(Base):
    __tablename__ = "company_engagements"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    position = Column(String)
    company_url = Column(String)
    person_id = Column(Integer, ForeignKey('persons.id'))
    person = relationship("Person", back_populates="companies")