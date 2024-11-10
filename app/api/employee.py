from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, utils, database, oauth2
from oauth2 import get_current_user
from schemas import BranchCreate, BranchResponse, UserCreate
from utils import hash
from database import get_db
from fastapi import Query

router = APIRouter(
    prefix="/employee",
    tags=["Employee"]
    # dependencies=[Depends(oauth2.get_current_user)]
)



@router.post("/apply-leave/", response_model=schemas.LeaveApplicationResponse)
def apply_leave(leave_date: date, reason: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check if there’s already an application for that date
    existing_leave = db.query(models.LeaveApplication).filter(
        models.LeaveApplication.user_id == current_user.user_id,
        models.LeaveApplication.leave_date == leave_date
    ).first()
    
    if existing_leave:
        raise HTTPException(status_code=400, detail="Leave already applied for this date")

    leave_application = models.LeaveApplication(
        user_id=current_user.user_id,
        leave_date=leave_date,
        reason=reason
    )

    db.add(leave_application)
    db.commit()
    db.refresh(leave_application)

    return leave_application
