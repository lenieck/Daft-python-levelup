from hashlib import sha256
from hashlib import sha512
from fastapi import FastAPI, Cookie, Depends
from fastapi import FastAPI, Response, status
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException
from typing import Optional
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI()
app.counter = 0
app.patients = dict()

@app.post("/method", status_code = 201)
def POST():
    return {"method": "POST"}

@app.get("/")
def root():
    return {"message": "Hello world!"}

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
    vacc_days = 0
    for i in patient.name + patient.surname:
        if i.isalpha():
            vacc_days += 1
    vacc_date = datetime.today() + timedelta(days=vacc_days)
    vacc_date = vacc_date.strftime('%Y-%m-%d')
    patient_data = Patient(id=app.counter, name=patient.name, surname=patient.surname, register_date=register_date, vaccination_date=vacc_date)
    app.patients[app.counter] = dict(patient_data)
    return patient_data

@app.get("/patient/{id}",status_code=200)
def patient_view(id: int):
    id = int(id)
    if id in app.patients:
        patient = app.patients[id]
        response = Patient(
            id=id,
            name=patient['name'],
            surname=patient['surname'],
            register_date=patient['register_date'],
            vaccination_date=patient['vaccination_date']
        )
        return response
    elif id < 1:
        raise HTTPException(status_code=400)
    else:
        raise HTTPException(status_code=404)

security = HTTPBasic()
app.secret_key = "very constant and random secret, best 64+ characters"
app.access_tokens = []
app.login_tokens = []

@app.post("/login_session", status_code=201)
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == "4dm1n" or credentials.password == "NotSoSecurePa$$":
        session_token = sha256(f"4dm1nNotSoSecurePa$${app.secret_key}".encode()).hexdigest()
        app.access_tokens.append(session_token)
        response.set_cookie(key="session_token", value=session_token)
    else:
        response.status_code = 401
        raise HTTPException(status_code=401)

@app.post("/login_token", status_code=201)
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == "4dm1n" or credentials.password == "NotSoSecurePa$$":
        session_token = sha256(f"4dm1nNotSoSecurePa$${app.secret_key}".encode()).hexdigest()
        app.login_tokens.append(session_token)
    else:
        response.status_code = 401
        raise HTTPException(status_code=401)
    return {"token": session_token}


@app.get("/welcome_session", status_code=200)
def welcome_session(response: Response, session_token: str = Cookie(None), format: str = ""):
    if (session_token not in app.access_tokens) or (session_token == ""):
        raise HTTPException(status_code=401)
    if format == 'json':
        return {"message": "Welcome!"}
    elif format == 'html':
        return HTMLResponse(content="<h1>Welcome!</h1>")
    else:
        return PlainTextResponse(content="Welcome!")


@app.get("/welcome_token", status_code=200)
def welcome_token(response: Response, token: str, format: str = ""):
    if (token not in app.login_tokens) or (token == ""):
        raise HTTPException(status_code=401)
    if format == 'json':
        return {"message": "Welcome!"}
    elif format == 'html':
        return HTMLResponse(content="<h1>Welcome!</h1>")
    else:
        return PlainTextResponse(content="Welcome!")

@app.get("/hello", response_class=HTMLResponse)
def hello():
    return f"""
    <html>
         <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Hello! Today date is {datetime.today().strftime('%Y-%m-%d')}</h1>
        </body>
    </html>
    """
