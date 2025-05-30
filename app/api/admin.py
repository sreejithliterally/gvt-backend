from datetime import date, datetime
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
    prefix="/admin",
    tags=["Admin"]
    # dependencies=[Depends(oauth2.get_current_user)]
)

def admin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


@router.get("/attendance/date", response_model=List[schemas.AttendanceResponse])
def get_attendance_by_date(
    attendance_date: date = Query(..., description="The date to retrieve attendance records for"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_required)
):  
    # Query attendance records for all users on the specified date
    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.date == attendance_date
    ).all()

    if not attendance_records:
        raise HTTPException(status_code=404, detail="No attendance records found for this date")

    return attendance_records
@router.post("/create_user", response_model=schemas.UserOut)
def create_user(
    user: UserCreate, 
    db: Session = Depends(database.get_db), 
    # current_user: models.User = Depends(admin_required)
):
    existing_user = db.query(models.User).filter(
         (models.User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    
    new_user = models.User(
        first_name=user.first_name,
        last_name = user.last_name,
        email=user.email,
        hashed_password=hash(user.password),
        role_id=user.role_id,
        branch_id=user.branch_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    role_name = db.query(models.Role.role_name).filter(models.Role.role_id == new_user.role_id).scalar()

    response = {
        "user_id": new_user.user_id,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "email": new_user.email,
        "branch_id": new_user.branch_id,
        "role_name": role_name  
    }
    return response






@router.get("/users", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found.")

    user_list = []
    for user in users:
        role_name = db.query(models.Role.role_name).filter(models.Role.role_id == user.role_id).scalar()
        user_list.append({
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "branch_id": user.branch_id,
            "role_name": role_name
        })

    return user_list

@router.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    
    role_name = db.query(models.Role.role_name).filter(models.Role.role_id == user.role_id).scalar()

    return {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "branch_id": user.branch_id,
        "role_name": role_name
    }

@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(admin_required)):
    user_in_db = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user_in_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_in_db.first_name = user.first_name
    user_in_db.last_name = user.last_name
    user_in_db.email = user.email
    user_in_db.role_id = user.role_id
    user_in_db.branch_id = user.branch_id

    db.commit()
    db.refresh(user_in_db)

    role_name = db.query(models.Role.role_name).filter(models.Role.role_id == user_in_db.role_id).scalar()

    return {
        "user_id": user_in_db.user_id,
        "first_name": user_in_db.first_name,
        "last_name": user_in_db.last_name,
        "email": user_in_db.email,
        "branch_id": user_in_db.branch_id,
        "role_name": role_name
    }
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(admin_required)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"detail": f"User with ID {user_id} deactivated"}



@router.post("/mark-attendance/", response_model=schemas.AttendanceResponse)
def mark_attendance(
    user_id: int,
    attendance_date: date,
    status: str,  # Acceptable values: 'present', 'absent', 'leave'
    db: Session = Depends(get_db),
    # Dependency to ensure only admins can access
):
    # Validate attendance status
    if status not in ["present", "absent", "leave"]:
        raise HTTPException(status_code=400, detail="Invalid attendance status")

    # Check if attendance record already exists for the user and date
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.user_id == user_id,
        models.Attendance.date == attendance_date
    ).first()

    if existing_attendance:
        raise HTTPException(status_code=400, detail="Attendance already marked for this date")

    # Create new attendance record
    attendance = models.Attendance(
        user_id=user_id,
        date=attendance_date,
        status=status,
        created_at=datetime.utcnow()
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance


@router.get("/attendance/{user_id}", response_model=List[schemas.AttendanceResponse])
def get_employee_attendance(
    user_id: int,
    db: Session = Depends(get_db),
):
    # Query attendance records for the specified user
    attendance_records = db.query(models.Attendance).filter(
        models.Attendance.user_id == user_id
    ).all()

    if not attendance_records:
        raise HTTPException(status_code=404, detail="No attendance records found for this employee")

    return attendance_records


@router.get("/leave-requests-pending/", response_model=List[schemas.LeaveRequestPendingResponse])
def get_pending_leave_requests(
    db: Session = Depends(get_db)
):
    # Query for pending leave applications along with user details
    pending = (
        db.query(
            models.LeaveApplication.leave_id,
            models.LeaveApplication.user_id,
            models.LeaveApplication.leave_date,
            models.LeaveApplication.reason,
            models.LeaveApplication.status,
            models.LeaveApplication.created_at,
            models.User.first_name,
            models.User.last_name
        )
        .join(models.User, models.LeaveApplication.user_id == models.User.user_id)
        .filter(models.LeaveApplication.status == 'pending')
        .all()
    )

    if not pending:
        raise HTTPException(status_code=404, detail="No pending leave applications found")

    # Convert query result to list of dictionaries
    return [
        {
            "leave_id": record.leave_id,
            "user_id": record.user_id,
            "leave_date": record.leave_date,
            "reason": record.reason,
            "status": record.status,
            "created_at": record.created_at,
            "first_name": record.first_name,
            "last_name": record.last_name,
        }
        for record in pending
    ]


@router.get("/leave-details/{leave_id}", response_model=schemas.LeaveRequestPendingResponse)
def get_leave_details(
    leave_id: int,
    db: Session = Depends(get_db)
):
    # Query for the specific leave application and user details
    leave_details = (
        db.query(
            models.LeaveApplication.leave_id,
            models.LeaveApplication.leave_date,
            models.LeaveApplication.reason,
            models.LeaveApplication.status,
            models.LeaveApplication.created_at,
            models.User.user_id,
            models.User.first_name,
            models.User.last_name
        )
        .join(models.User, models.LeaveApplication.user_id == models.User.user_id)
        .filter(models.LeaveApplication.leave_id == leave_id)
        .first()
    )

    if not leave_details:
        raise HTTPException(status_code=404, detail="Leave application not found")

    # Return the details in the expected format
    return {
        "leave_id": leave_details.leave_id,
        "leave_date": leave_details.leave_date,
        "reason": leave_details.reason,
        "status": leave_details.status,
        "created_at": leave_details.created_at,
        "user_id": leave_details.user_id,
        "first_name": leave_details.first_name,
        "last_name": leave_details.last_name,
    }


@router.put("/leave-requests/{leave_id}/status")
def update_leave_status(
    leave_id: int,
    status_update: schemas.LeaveStatusUpdate,
    db: Session = Depends(get_db)
):
    # Validate the status value
    if status_update.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=400, detail="Invalid status. Choose 'approved' or 'rejected'."
        )

    # Fetch the leave application by ID
    leave_request = db.query(models.LeaveApplication).filter(
        models.LeaveApplication.leave_id == leave_id
    ).first()

    if not leave_request:
        raise HTTPException(
            status_code=404, detail="Leave application not found"
        )

    # Update the status
    leave_request.status = status_update.status
    db.commit()
    db.refresh(leave_request)

    return {
        "leave_id": leave_request.leave_id,
        "status": leave_request.status,
        "message": f"Leave request has been {leave_request.status}.",
    }
