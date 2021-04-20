from fastapi import FastAPI

app = FastAPI()

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
    if password == False or password_hash == False:
        raise HTTPException(status_code=401)
    password = password.encode()
    if sha512(password).hexdigest() != password_hash:
        raise HTTPException(status_code=401)
