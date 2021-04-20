from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from hashlib import sha512
from typing import Optional

app = FastAPI()
app.counter = 0

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
        
@app.post("/register", status_code=201)
def register(patient: Patient):
    app.counter += 1
    today = date.today()
    register_date = str(today)
    name_length = len([i for i in patient.name if i.isalpha()])
    surname_length = len([i for i in patient.surname if i.isalpha()])
    vaccination_date = today + timedelta(days=(name_length + surname_length))
    return {"id": app.counter, "name:":  patient.name, "surname:": patient.surname, "register_date": register_date, "vaccination_date": vaccination_date}
