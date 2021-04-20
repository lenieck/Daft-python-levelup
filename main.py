from fastapi import FastAPI
from fastapi import FastAPI, Response, status
from fastapi import FastAPI, HTTPException
from hashlib import sha512
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()
app.counter = 0
app.patients = dict()

@app.get("/")
def root():
    return {"message": "Hello world!"}

@app.post("/method", status_code = 201)
def POST():
    return {"method": "POST"}

@app.get("/method")
def GET():
    return {"method": "GET"}

@app.delete("/method")
def DELETE():
    return {"method": "DELETE"}

@app.put("/method")
def PUT():
    return {"method": "PUT"}

@app.options("/method")
def OPTIONS():
    return {"method": "OPTIONS"}

@app.get('/auth', status_code=204)
def auth(password: Optional[str] = None, password_hash: Optional[str] = None):
    if password == None or password_hash == None or password == "" or password_hash == "":
        raise HTTPException(status_code=401)
    password = password.encode()
    if sha512(password).hexdigest() != password_hash:
        raise HTTPException(status_code=401)
        
class PatientRegister(BaseModel):
    name: str
    surname: str

class Patient(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str

@app.post("/register", status_code=201)
def register(patient: PatientRegister):
    app.counter += 1
    register_date = datetime.today().strftime('%Y-%m-%d')
    Patient.register_date = register_date
    vacc_days = len([i for i in patient.name+patient.surname if i.isalpha()])
    vacc_date = datetime.today() + timedelta(days=vacc_days)
    vacc_date = vacc_date.strftime('%Y-%m-%d')
    patient_data = Patient(id=app.counter, name=patient.name, surname=patient.surname, register_date=register_date, vaccination_date=vacc_date)
    app.patients[app.counter] = patient_data
    return patient_data

'''
@app.get("/patient/{id}",status_code=200)
def patient_view(id: int):
    if id > 0 and id <= app.counter:
    elif id < 1:
        raise HTTPException(status_code=400)
    elif id > app.counter:
        raise HTTPException(status_code=404)
'''
