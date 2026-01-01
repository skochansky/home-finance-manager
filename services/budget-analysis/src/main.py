from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
import httpx
import pandas as pd
import numpy as np

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/budget_analysis")
TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8001")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="HFM Budget Analysis Service", version="0.1.0")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    category = Column(String)
    amount = Column(Float)
    period = Column(String)  # monthly, weekly, yearly
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class BudgetAlert(Base):
    __tablename__ = "budget_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"))
    user_id = Column(Integer, index=True)
    alert_type = Column(String)  # overspent, approaching_limit, goal_reached
    message = Column(Text)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Integer, default=0)

class BudgetCreate(BaseModel):
    name: str
    category: str
    amount: float
    period: str
    start_date: datetime
    end_date: datetime

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: str
    amount: float
    period: str
    start_date: datetime
    end_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class BudgetAnalysis(BaseModel):
    budget_id: int
    budget_name: str
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    percentage_used: float
    days_remaining: int
    status: str  # on_track, at_risk, over_budget

class SpendingInsight(BaseModel):
    category: str
    total_spent: float
    transaction_count: int
    average_transaction: float
    trend: str  # increasing, decreasing, stable

async def get_user_transactions(user_id: int, start_date: datetime, end_date: datetime):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TRANSACTION_SERVICE_URL}/transactions/{user_id}",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        if response.status_code == 200:
            return response.json()
        return []

@app.get("/")
def read_root():
    return {"service": "HFM Budget Analysis Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/budgets", response_model=BudgetResponse)
def create_budget(budget: BudgetCreate, user_id: int):
    db = SessionLocal()
    try:
        db_budget = Budget(**budget.dict(), user_id=user_id)
        db.add(db_budget)
        db.commit()
        db.refresh(db_budget)
        return db_budget
    finally:
        db.close()

@app.get("/budgets/{user_id}", response_model=List[BudgetResponse])
def get_user_budgets(user_id: int):
    db = SessionLocal()
    try:
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        return budgets
    finally:
        db.close()

@app.get("/budgets/{user_id}/analysis", response_model=List[BudgetAnalysis])
async def analyze_budgets(user_id: int):
    db = SessionLocal()
    try:
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        analyses = []
        
        for budget in budgets:
            # Get transactions for this budget period and category
            transactions = await get_user_transactions(
                user_id, budget.start_date, budget.end_date
            )
            
            # Filter transactions by category if specified
            category_transactions = [
                t for t in transactions 
                if t.get('category', '').lower() == budget.category.lower()
            ]
            
            spent_amount = sum(t.get('amount', 0) for t in category_transactions)
            remaining_amount = budget.amount - spent_amount
            percentage_used = (spent_amount / budget.amount) * 100 if budget.amount > 0 else 0
            
            days_remaining = (budget.end_date - datetime.utcnow()).days
            
            # Determine status
            if percentage_used >= 100:
                status = "over_budget"
            elif percentage_used >= 80:
                status = "at_risk"
            else:
                status = "on_track"
            
            analyses.append(BudgetAnalysis(
                budget_id=budget.id,
                budget_name=budget.name,
                budget_amount=budget.amount,
                spent_amount=spent_amount,
                remaining_amount=remaining_amount,
                percentage_used=percentage_used,
                days_remaining=max(0, days_remaining),
                status=status
            ))
        
        return analyses
    finally:
        db.close()

@app.get("/insights/{user_id}/spending", response_model=List[SpendingInsight])
async def get_spending_insights(user_id: int, days: int = 30):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    transactions = await get_user_transactions(user_id, start_date, end_date)
    
    if not transactions:
        return []
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(transactions)
    if df.empty:
        return []
    
    # Group by category
    category_analysis = df.groupby('category').agg({
        'amount': ['sum', 'count', 'mean']
    }).round(2)
    
    insights = []
    for category in category_analysis.index:
        total_spent = float(category_analysis.loc[category, ('amount', 'sum')])
        transaction_count = int(category_analysis.loc[category, ('amount', 'count')])
        average_transaction = float(category_analysis.loc[category, ('amount', 'mean')])
        
        # Simple trend analysis (could be enhanced)
        trend = "stable"  # Placeholder - would need historical data for real trend analysis
        
        insights.append(SpendingInsight(
            category=category,
            total_spent=total_spent,
            transaction_count=transaction_count,
            average_transaction=average_transaction,
            trend=trend
        ))
    
    # Sort by total spent descending
    insights.sort(key=lambda x: x.total_spent, reverse=True)
    
    return insights

@app.post("/budgets/{budget_id}/alerts")
def create_budget_alert(budget_id: int, alert_type: str, message: str):
    db = SessionLocal()
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        
        alert = BudgetAlert(
            budget_id=budget_id,
            user_id=budget.user_id,
            alert_type=alert_type,
            message=message
        )
        db.add(alert)
        db.commit()
        return {"message": "Alert created successfully"}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)