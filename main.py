from fastapi import FastAPI
from fastapi import FastAPI, Response, status
from fastapi import FastAPI, HTTPException
from hashlib import sha512
from typing import Optional
from datetime import date, timedelta
from pydantic import BaseModel

app = FastAPI()
app.counter = 0
patients = [[], [], [], [], []]

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
        
class Patient(BaseModel):
    name: str
    surname: str

@app.post("/register", status_code=201)
def register(patient: Patient):
    app.counter += 1
    today = date.today()
    register_date = str(today)
    name_length = len([i for i in patient.name if i.isalpha()])
    surname_length = len([i for i in patient.surname if i.isalpha()])
    vaccination_date = today + timedelta(days=(name_length + surname_length))
    patients[0].append(int(app.counter))
    patients[1].append(patient.name)
    patients[2].append(patient.surname)
    patients[3].append(str(register_date))
    patients[4].append(str(vaccination_date))
    return {"id": app.counter, "name:":  patient.name, "surname:": patient.surname, "register_date": register_date, "vaccination_date": vaccination_date}

@app.get("/patient/{id}",status_code=200)
def patient_view(id: int):
    if id > 0 and id <= app.counter:
        return {"id": id, "name:":  patients[1][id-1], "surname:": patients[2][id-1], "register_date": patients[3][id-1], "vaccination_date": patients[4][id-1]}
    elif id < 1:
        raise HTTPException(status_code=400)
    elif id > app.counter:
        raise HTTPException(status_code=404)
