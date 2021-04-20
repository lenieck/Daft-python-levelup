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
def register(pacjent: Patient):
    app.counter += 1
    name_len = 0
    surname_len = 0
    today = date.today()
    for i in range(len(pacjent.name)):
        if (pacjent.name[i].isalpha()):
            name_len += 1
    for i in range(len(pacjent.surname)):
        if (pacjent.surname[i].isalpha()):
            surname_len += 1

    all_len = name_len + surname_len

    vacc_date = today + timedelta(days=all_len)
    d1 = today.strftime("%Y-%m-%d")
    return {"id": app.counter, **pacjent.dict(), "register_date": d1, "vaccination_date": vacc_date}

@app.get("/patient/{id}",status_code=200)
def patient_view(id: int):
    if id > 0 and id <= app.counter:
        return {"id": id, "name:":  patients[1][id-1], "surname:": patients[2][id-1], "register_date": patients[3][id-1], "vaccination_date": patients[4][id-1]}
    elif id < 1:
        raise HTTPException(status_code=400)
    elif id > app.counter:
        raise HTTPException(status_code=404)
