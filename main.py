from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database configuration
DATABASE_URL = "postgresql+psycopg2://doadmin:AVNS_ZAUb1Xd5Glnl9r2OMBU@panorah-do-user-17039258-0.h.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database models
class DocType(Base):
    __tablename__ = "doctype"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    fields = relationship("DocField", back_populates="parent")

class DocField(Base):
    __tablename__ = "docfield"
    
    id = Column(String, primary_key=True, index=True)
    fieldname = Column(String, index=True)
    fieldlabel = Column(String)
    fieldtype = Column(String)
    parent_id = Column(String, ForeignKey("doctype.id"))
    parent = relationship("DocType", back_populates="fields")

# Create tables
Base.metadata.create_all(bind=engine)

# Define Pydantic models
class DocTypeCreate(BaseModel):
    name: str

class DocFieldCreate(BaseModel):
    fieldname: str
    fieldlabel: str
    fieldtype: str
    parent_id: str

app = FastAPI()

@app.post("/doctype/", response_model=DocTypeCreate)
def create_doctype(doctype: DocTypeCreate):
    db = SessionLocal()
    db_doctype = DocType(name=doctype.name)
    db.add(db_doctype)
    db.commit()
    db.refresh(db_doctype)
    db.close()
    return db_doctype

@app.post("/docfield/", response_model=DocFieldCreate)
def create_docfield(docfield: DocFieldCreate):
    db = SessionLocal()
    db_docfield = DocField(
        fieldname=docfield.fieldname,
        fieldlabel=docfield.fieldlabel,
        fieldtype=docfield.fieldtype,
        parent_id=docfield.parent_id
    )
    db.add(db_docfield)
    db.commit()
    db.refresh(db_docfield)
    db.close()
    return db_docfield

@app.get("/doctype/{doctype_id}")
def read_doctype(doctype_id: str):
    db = SessionLocal()
    doctype = db.query(DocType).filter(DocType.id == doctype_id).first()
    db.close()
    if doctype is None:
        raise HTTPException(status_code=404, detail="DocType not found")
    return doctype

@app.get("/docfield/{docfield_id}")
def read_docfield(docfield_id: str):
    db = SessionLocal()
    docfield = db.query(DocField).filter(DocField.id == docfield_id).first()
    db.close()
    if docfield is None:
        raise HTTPException(status_code=404, detail="DocField not found")
    return docfield

# Run the server with: uvicorn main:app --reload
