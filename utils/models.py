from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    department = Column(String(50))
    batch = Column(Integer)
    cgpa = Column(Float)
    backlogs = Column(Integer, default=0)
    attendance = Column(Float, default=75.0)
    internships = Column(Integer, default=0)
    projects = Column(Integer, default=0)
    certifications = Column(Integer, default=0)
    hackathons = Column(Integer, default=0)
    communication_score = Column(Float, default=7.0)
    aptitude_score = Column(Float, default=7.0)
    lms_activity = Column(Float, default=70.0)
    skills = Column(JSON, default=list)
    mock_interview_scores = Column(JSON, default=list)
    avg_mock_score = Column(Float, default=0.0)
    readiness_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    placements = relationship("Placement", back_populates="student")

class SkillProgram(Base):
    __tablename__ = "skill_programs"
    id = Column(Integer, primary_key=True)
    program_id = Column(String(20), unique=True)
    name = Column(String(100))
    duration_weeks = Column(Integer)
    hours = Column(Integer)
    cost = Column(Float)
    modules = Column(JSON, default=list)
    skills_covered = Column(JSON, default=list)
    delivery_model = Column(String(20))
    has_internship = Column(Boolean, default=False)
    has_mentorship = Column(Boolean, default=False)
    completion_rate = Column(Float, default=0.8)
    avg_feedback_score = Column(Float, default=4.0)
    industry_relevance = Column(Float, default=8.0)

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    industry = Column(String(50))
    tier = Column(Integer, default=2)
    required_skills = Column(JSON, default=list)
    avg_package = Column(Float)
    salary_band_min = Column(Float)
    salary_band_max = Column(Float)
    hiring_trend = Column(String(20))
    placements = relationship("Placement", back_populates="company")

class Placement(Base):
    __tablename__ = "placements"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    role = Column(String(100))
    salary = Column(Float)
    placement_date = Column(DateTime)
    is_internship_conversion = Column(Boolean, default=False)
    student = relationship("Student", back_populates="placements")
    company = relationship("Company", back_populates="placements")

class IndustryRequirement(Base):
    __tablename__ = "industry_requirements"
    id = Column(Integer, primary_key=True)
    role = Column(String(100), unique=True)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    min_cgpa = Column(Float, default=6.5)
    avg_salary = Column(Float)
    demand_score = Column(Float)
    growth_rate = Column(Float)
    companies_hiring = Column(JSON, default=list)

class AgentLog(Base):
    __tablename__ = "agent_logs"
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(100))
    input_data = Column(JSON)
    output_data = Column(JSON)
    execution_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
