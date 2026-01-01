from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/transactions")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="HFM Transaction Management Service", version="0.1.0")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    account_id = Column(Integer, index=True)
    amount = Column(Float)
    category = Column(String)
    description = Column(String)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class TransactionCreate(BaseModel):
    user_id: int
    account_id: int
    amount: float
    category: str
    description: str
    transaction_date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    amount: float
    category: str
    description: str
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"service": "HFM Transaction Management Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate):
    db = SessionLocal()
    try:
        db_transaction = Transaction(**transaction.dict())
        if transaction.transaction_date is None:
            db_transaction.transaction_date = datetime.utcnow()
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    finally:
        db.close()

@app.get("/transactions/{user_id}", response_model=List[TransactionResponse])
def get_user_transactions(user_id: int):
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
        return transactions
    finally:
        db.close()

@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int):
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)