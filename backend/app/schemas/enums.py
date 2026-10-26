from enum import Enum


class UserType(str, Enum):
    student = "student"
    faculty = "faculty"


class EmploymentStatus(str, Enum):
    pending = "pending"
    active = "active"
    inactive = "inactive"


class AdminRole(str, Enum):
    admin = "admin"


class AppRole(str, Enum):
    admin = "admin"
    maintenance = "maintenance"
    student = "student"
    faculty = "faculty"
