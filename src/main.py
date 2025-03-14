from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
