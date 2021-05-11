from hashlib import sha256
from hashlib import sha512
from fastapi import FastAPI, Cookie, Depends, Response, status, HTTPException
from typing import Optional
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3



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


@app.delete("/logout_session")
def logout_session(session_token: str = Cookie(None), format: str = ""):
    if (session_token not in app.access_tokens) and (session_token not in app.login_tokens):
        raise HTTPException(status_code=401)
    if session_token in app.access_tokens:
        app.access_tokens.remove(session_token)
    else:
        app.login_tokens.remove(session_token)
    return RedirectResponse(url=f"/logged_out?format={format}", status_code=302)

@app.delete("/logout_token")
def logout_token(token: str, format: str = ""):
    if ((token not in app.login_tokens) and (token not in app.access_tokens)) or (token == ""):
        raise HTTPException(status_code=401)
    if token in app.login_tokens:
        app.login_tokens.remove(token)
    else:
        app.access_tokens.remove(token)
    return RedirectResponse(url=f"/logged_out?format={format}", status_code=302)

@app.get("/logged_out", status_code=200)
def logged_out(format: str = ""):
    if format == 'json':
        return {"message": "Logged out!"}
    elif format == 'html':
        return HTMLResponse(content="<h1>Logged out!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Logged out!", status_code=200)
'''
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
'''
#-----------------------4-----------------------

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/categories")
async def categories():
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    data = cursor.execute("""
                          SELECT CategoryID, CategoryName
                          FROM Categories
                          ORDER BY CategoryID;
                          """).fetchall()
    result = {"categories": [{"id": x["CategoryID"],
             "name": x["CategoryName"]
             } 
            for x in data]}
    return result
    
@app.get("/customers")
async def customers():
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    data = cursor.execute("""
                          SELECT CustomerID, CompanyName, COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || COALESCE(City, '') || ' ' || COALESCE(Country, '') As FullAddress
                          FROM Customers
                          ORDER BY CustomerID COLLATE NOCASE;
                          """).fetchall()
    
    result = {"customers": [{"id": x["CustomerID"],
             "name": x["CompanyName"],
             "full_address": x["FullAddress"]
             }
            for x in data]}
    return result
