from hashlib import sha256
from hashlib import sha512
from fastapi import FastAPI, Cookie, Depends, Response, status, HTTPException
from typing import Optional
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3
  
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func, update
from fastapi import HTTPException

# from . import models
import models
import schemas



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
    app.dbc = sqlite3.connect("northwind.db")
    app.dbc.text_factory = lambda b: b.decode(errors='ignore')


@app.on_event("shutdown")
async def shutdown():
    app.dbc.close()


@app.get("/categories")
async def get_categories():
    cursor = app.dbc.cursor()
    categories = cursor.execute("SELECT  CategoryID, CategoryName FROM Categories ORDER BY CategoryID").fetchall()
    result = dict(categories=[dict(id=row[0], name=row[1]) for row in categories])
    return result


@app.get("/customers")
async def get_customers():
    cursor = app.dbc.cursor()
    cursor.row_factory = sqlite3.Row
    customers = cursor.execute(
        "SELECT CustomerID id, COALESCE(CompanyName, '') name, "
        "COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || COALESCE(City, '') || ' ' || "
        "COALESCE(Country, '') full_address "
        "FROM Customers c ORDER BY UPPER(CustomerID);"
    ).fetchall()
    return dict(customers=customers)


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return db.query(models.Supplier)\
             .order_by(models.Supplier.SupplierID.asc())\
             .all()


def get_supplier(db: Session, id: int):
    return (
        db.query(models.Supplier)
          .filter(models.Supplier.SupplierID == id)
          .first()
    )


def get_products_from_supplier(db: Session, id: int):
    return (
        db.query(models.Product)
            .filter(models.Product.SupplierID == id)
            .order_by(models.Product.ProductID.desc())
            .all()
    )


def create_supplier(db: Session, new_supplier: schemas.NewSupplier):
    highest_id = db.query(func.max(models.Supplier.SupplierID)).scalar()
    new_supplier.SupplierID = highest_id + 1
    db.add(models.Supplier(**new_supplier.dict()))
    db.commit()
    return get_supplier(db, highest_id + 1)


def update_supplier(db: Session, id: int, supplier_update: schemas.SupplierUpdate):
    properties_to_update = {key: value for key, value in supplier_update.dict().items() if value is not None}
    update_statement = update(models.Supplier) \
                       .where(models.Supplier.SupplierID == id) \
                       .values(**properties_to_update)
    db.execute(update_statement)
    db.commit()
    return get_supplier(db, id)


def delete_supplier(db: Session, id: int):
    check_supplier = get_supplier(db, id)
    if not check_supplier:
        raise HTTPException(status_code=404)
    db.query(models.Supplier)\
      .filter(models.Supplier.SupplierID == id)\
      .delete()
    db.commit()
@app.get("/products/{id}")
async def get_product(id: int):
    if not isinstance(id, int):
        raise HTTPException(status_code=404, detail="Wrong")
    cursor = app.dbc.cursor()
    cursor.row_factory = sqlite3.Row
    product = cursor.execute(
        "SELECT ProductID id, RTRIM(ProductName) name FROM Products p WHERE ProductID = ?",
        (id,)
    ).fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Wrong")
    return product

emp_orders = {'last_name': 'LastName',
              'first_name': 'FirstName',
              'city': 'City',
              'EmployeeID': 'EmployeeID',
              '': "EmployeeID"}

@app.get("/employees")
async def get_employees(limit: int = -1, offset: int = 0, order: str = ''):
    order = order.strip()
    if not (isinstance(limit, int) and isinstance(offset, int) and order in emp_orders.keys()):
        raise HTTPException(status_code=400)
    cursor = app.dbc.cursor()
    cursor.row_factory = sqlite3.Row
    employees = cursor.execute(
        "SELECT EmployeeID id, LastName last_name, FirstName first_name, City city "
        f"FROM Employees ORDER BY {emp_orders[order]} LIMIT :lim OFFSET :off;"
        , {"lim": limit, "off": offset}
    ).fetchall()
    return dict(employees=employees)

@app.get("/products_extended")
async def products_extended(response: Response):
    response.status_code = 200
    cursor = app.dbc.cursor()
    cursor.row_factory = sqlite3.Row
    result = cursor.execute(
        '''SELECT p.ProductID id, p.ProductName name, c.CategoryName category, s.CompanyName supplier
           FROM Products p 
           JOIN Categories c ON p.CategoryID = c.CategoryID 
           JOIN Suppliers s ON p.SupplierID = s.SupplierID''').fetchall()
    return {"products_extended": result}


@app.get("/products/{id}/orders")
async def order_details(response: Response, id: int):
    response.status_code = 200
    cursor = app.dbc.cursor()
    cursor.row_factory = sqlite3.Row
    result = cursor.execute(
        '''SELECT o.OrderID id, c.CompanyName customer, od.Quantity quantity,ROUND((od.UnitPrice * od.Quantity) - od.Discount * (od.UnitPrice * od.Quantity),2) total_price
           FROM Orders o JOIN Customers c ON o.CustomerID = c.CustomerID JOIN "Order Details" od ON o.OrderID = od.OrderID	
           WHERE od.ProductID = :id
        ''', {"id": id}).fetchall()
    if result:
        return {"orders": result}
    raise HTTPException(status_code=404)

class Category(BaseModel):
    name: str

class CreatedCategory(BaseModel):
    id: int
    name: str

@app.post("/categories", status_code=201, response_model=CreatedCategory)
async def create_category(category: Category):
    cursor = app.dbc.execute(
        "INSERT INTO Categories (CategoryName) VALUES (?)", (category.name, ))
    app.dbc.commit()
    return {"id": cursor.lastrowid,
            "name": category.name}


@app.put("/categories/{id}", status_code=200, response_model=CreatedCategory)
async def modify_category(category: Category, id: int):
    cursor = app.dbc.execute(
        "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?", (category.name, id)
    )
    app.dbc.commit()
    cursor.row_factory = sqlite3.Row
    cat = cursor.execute(
        '''SELECT c.CategoryID id, c.CategoryName name 
            FROM Categories c 
            WHERE c.CategoryID = :id''', {"id": id}).fetchone()
    if cat:
        return cat
    raise HTTPException(status_code=404)


@app.delete("/categories/{id}", status_code=200)
async def delete_category(id: int):
    cursor = app.dbc.execute(
        '''SELECT c.CategoryID 
            FROM Categories c 
            WHERE c.CategoryID = :id''', {'id': id})
    if not cursor.fetchone():
        raise HTTPException(status_code=404)
    cursor.execute(
        '''DELETE FROM Categories 
            WHERE categoryID = :id''', {"id": id})
    app.dbc.commit()
    return {"deleted": 1}
