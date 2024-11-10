from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, DECIMAL, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import database
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Branch(database.Base):
    __tablename__ = "branches"

    branch_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    branch_manager = Column(String, nullable=False)

    users = relationship("User", back_populates="branch")

class Role(database.Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True)


class User(database.Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role_id = Column(Integer, ForeignKey('roles.role_id'))
    branch_id = Column(Integer, ForeignKey('branches.branch_id'), nullable=True)  # Nullable for RTO/Admin who can access all branches
    is_active = Column(Boolean, default=True)

    branch = relationship("Branch", back_populates="users")
    attendances = relationship("Attendance", back_populates="user")
    leave_applications = relationship("LeaveApplication", back_populates="user")


class Attendance(database.Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # 'present', 'absent', 'leave'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="attendances")

class LeaveApplication(database.Base):
    __tablename__ = "leave_applications"

    leave_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    leave_date = Column(Date, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="pending")  # 'pending', 'approved', 'rejected'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="leave_applications")
