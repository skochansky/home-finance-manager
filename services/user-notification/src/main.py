from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
import os
import redis
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/notifications")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
redis_client = redis.from_url(REDIS_URL)

app = FastAPI(title="HFM User Notification Service", version="0.1.0")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(String)  # email, sms, push
    subject = Column(String)
    message = Column(Text)
    recipient = Column(String)  # email address, phone number, device token
    status = Column(String, default="pending")  # pending, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    budget_alerts = Column(Boolean, default=True)
    transaction_alerts = Column(Boolean, default=True)

class NotificationCreate(BaseModel):
    user_id: int
    type: str
    subject: str
    message: str
    recipient: str

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    subject: str
    message: str
    recipient: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True

class PreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    budget_alerts: Optional[bool] = None
    transaction_alerts: Optional[bool] = None

@app.get("/")
def read_root():
    return {"service": "HFM User Notification Service", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/notifications", response_model=NotificationResponse)
def create_notification(notification: NotificationCreate):
    db = SessionLocal()
    try:
        db_notification = Notification(**notification.dict())
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        
        # Queue notification for processing
        redis_client.lpush("notification_queue", json.dumps({
            "id": db_notification.id,
            "type": db_notification.type,
            "recipient": db_notification.recipient,
            "subject": db_notification.subject,
            "message": db_notification.message
        }))
        
        return db_notification
    finally:
        db.close()

@app.get("/notifications/{user_id}", response_model=List[NotificationResponse])
def get_user_notifications(user_id: int):
    db = SessionLocal()
    try:
        notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
        return notifications
    finally:
        db.close()

@app.get("/preferences/{user_id}")
def get_user_preferences(user_id: int):
    db = SessionLocal()
    try:
        prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if not prefs:
            # Create default preferences
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        return prefs
    finally:
        db.close()

@app.put("/preferences/{user_id}")
def update_user_preferences(user_id: int, preferences: PreferenceUpdate):
    db = SessionLocal()
    try:
        prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
        
        for field, value in preferences.dict(exclude_unset=True).items():
            setattr(prefs, field, value)
            
        db.commit()
        db.refresh(prefs)
        return prefs
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)