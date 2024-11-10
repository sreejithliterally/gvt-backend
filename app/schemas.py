from datetime import datetime, date
from pydantic import BaseModel, EmailStr,Field
from typing import Optional, List

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    role_id: int
    branch_id: Optional[int] = None

class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str]  # Assuming last_name is optional
    email: str
    branch_id: Optional[int]
    role_name: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
    


class TokenData(BaseModel):
    id: int




class BranchCreate(BaseModel):
    name: str
    address: str
    phone_number: str
    branch_manager: str

class BranchUpdate(BaseModel):
    name: str
    address: str
    phone_number: str
    branch_manager: str

# Schema for returning branch information
class Branch(BaseModel):
    branch_id: int
    name: str
    address: Optional[str]
    branch_manager: Optional[str]
    phone_number: Optional[str]

    class Config:
        orm_mode = True

class BranchResponse(BaseModel):
    branch_id: int
    name: str
    address: str
    phone_number: str
    branch_manager: str

    class Config:
        orm_mode = True


class LeaveApplicationBase(BaseModel):
    leave_date: date
    reason: Optional[str] = Field(None, max_length=500)

# Schema for creating a new leave application
class LeaveApplicationCreate(LeaveApplicationBase):
    pass

# Schema for response after creating a leave application
class LeaveApplicationResponse(LeaveApplicationBase):
    leave_id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class AttendanceBase(BaseModel):
    user_id: int
    date: date
    status: str  # Expected values: "present", "absent", or "leave"

# Schema for creating a new attendance record
class AttendanceCreate(AttendanceBase):
    pass

# Schema for retrieving an attendance record
class AttendanceResponse(AttendanceBase):
    attendance_id: int
    created_at: datetime

    class Config:
        orm_mode = True