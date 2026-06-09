"""
Seed Script — Populates database with 500 sample students
Run: python seed.py
"""
import sys, os, random
import numpy as np
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(".env")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from placement_ai.utils.models import Base, Student, SkillProgram, Company, Placement, IndustryRequirement
from placement_ai.utils.config import settings

random.seed(42)
np.random.seed(42)

SKILLS = ["Python","Java","JavaScript","React","Node.js","SQL","MongoDB","AWS","Docker","Kubernetes",
          "Machine Learning","Deep Learning","Data Analysis","Power BI","Tableau","Excel","Git","Linux",
          "REST APIs","GenAI","Cloud Computing","Cybersecurity","DevOps","Agile","Communication",
          "Problem Solving","Leadership"]

PROGRAMS = [
    {"id":"PROG001","name":"Full Stack Development","weeks":16,"hours":200,"cost":25000,"skills":["JavaScript","React","Node.js","SQL","Git"],"delivery":"live","internship":True},
    {"id":"PROG002","name":"Data Science & ML","weeks":20,"hours":240,"cost":35000,"skills":["Python","Machine Learning","Deep Learning","SQL"],"delivery":"live","internship":True},
    {"id":"PROG003","name":"Cloud Computing","weeks":12,"hours":160,"cost":20000,"skills":["AWS","Docker","Kubernetes","Linux","DevOps"],"delivery":"recorded","internship":False},
    {"id":"PROG004","name":"Cybersecurity","weeks":14,"hours":180,"cost":30000,"skills":["Cybersecurity","Linux","Python"],"delivery":"live","internship":False},
    {"id":"PROG005","name":"DevOps Engineering","weeks":18,"hours":220,"cost":22000,"skills":["Docker","Kubernetes","AWS","Git","Linux"],"delivery":"live","internship":True},
    {"id":"PROG006","name":"GenAI & LLM","weeks":12,"hours":150,"cost":40000,"skills":["Python","GenAI","Machine Learning","Deep Learning"],"delivery":"live","internship":False},
    {"id":"PROG007","name":"Business Analytics","weeks":8,"hours":100,"cost":12000,"skills":["Excel","Power BI","Tableau","SQL","Python"],"delivery":"recorded","internship":False},
    {"id":"PROG008","name":"Mobile Development","weeks":14,"hours":170,"cost":18000,"skills":["JavaScript","React","Git"],"delivery":"live","internship":True},
    {"id":"PROG009","name":"Data Engineering","weeks":16,"hours":200,"cost":28000,"skills":["Python","SQL","AWS","Docker"],"delivery":"live","internship":True},
]

COMPANIES = ["TCS","Infosys","Wipro","Accenture","Cognizant","HCL","Google","Amazon","Microsoft",
             "IBM","Deloitte","Capgemini","Tech Mahindra","Zoho","Freshworks","Flipkart","Swiggy","Razorpay","KPMG","PwC"]

DEPTS = ["CSE","IT","ECE","EEE","Mechanical","Civil"]
ROLES = ["Software Engineer","Data Scientist","ML Engineer","DevOps Engineer","Full Stack Developer",
         "Cloud Architect","Security Analyst","Business Analyst","AI Engineer"]

def seed():
    engine = create_engine(settings.SYNC_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        # Companies
        company_map = {}
        for name in COMPANIES:
            c = db.query(Company).filter_by(name=name).first()
            if not c:
                c = Company(name=name, industry="IT", tier=random.randint(1,3),
                    required_skills=random.sample(SKILLS, random.randint(4,8)),
                    avg_package=random.randint(400000,1500000),
                    salary_band_min=random.randint(300000,500000),
                    salary_band_max=random.randint(800000,2000000),
                    hiring_trend=random.choice(["growing","stable","declining"]))
                db.add(c); db.flush()
            company_map[name] = c

        # Programs
        for p in PROGRAMS:
            if not db.query(SkillProgram).filter_by(program_id=p["id"]).first():
                db.add(SkillProgram(program_id=p["id"], name=p["name"],
                    duration_weeks=p["weeks"], hours=p["hours"], cost=p["cost"],
                    modules=[f"Module {i+1}" for i in range(random.randint(6,12))],
                    skills_covered=p["skills"], delivery_model=p["delivery"],
                    has_internship=p["internship"], has_mentorship=random.choice([True,False]),
                    completion_rate=round(random.uniform(0.7,0.95),2),
                    avg_feedback_score=round(random.uniform(3.5,4.8),1),
                    industry_relevance=round(random.uniform(7.0,9.5),1)))

        # Industry Requirements
        for role in ROLES:
            if not db.query(IndustryRequirement).filter_by(role=role).first():
                db.add(IndustryRequirement(role=role,
                    required_skills=random.sample(SKILLS, random.randint(5,8)),
                    preferred_skills=random.sample(SKILLS, random.randint(3,5)),
                    min_cgpa=round(random.uniform(6.0,7.5),1),
                    avg_salary=random.randint(500000,1500000),
                    demand_score=round(random.uniform(7.0,9.8),1),
                    growth_rate=round(random.uniform(0.05,0.30),2),
                    companies_hiring=random.sample(COMPANIES, random.randint(3,8))))

        # Students
        created = 0
        for i in range(500):
            sid = f"STU{2000+i:04d}"
            if db.query(Student).filter_by(student_id=sid).first():
                continue
            cgpa = round(max(4.0, min(10.0, np.random.normal(7.2, 0.9))), 2)
            backlogs = max(0, int(np.random.normal(0.5, 1.0)))
            internships = random.randint(0, 3)
            projects = random.randint(1, 6)
            certs = random.randint(0, 5)
            hackathons = random.randint(0, 4)
            communication = round(random.uniform(4, 10), 1)
            aptitude = round(random.uniform(4, 10), 1)
            attendance = round(random.uniform(60, 100), 1)
            lms = round(random.uniform(40, 100), 1)
            skills = random.sample(SKILLS, random.randint(4, 12))
            mock_scores = [random.randint(40, 100) for _ in range(random.randint(1, 5))]
            avg_mock = round(sum(mock_scores)/len(mock_scores), 1)
            readiness = round(min(100,
                0.3*(len(skills)/27*100) + 0.2*(cgpa/10*100) +
                0.2*(projects/6*100) + 0.1*(communication/10*100) +
                0.2*(internships/3*100)), 2)
            placed = random.random() < readiness/100

            s = Student(student_id=sid, name=f"Student {i+1}", email=f"student{i+1}@college.edu",
                department=random.choice(DEPTS), batch=random.choice([2021,2022,2023,2024]),
                cgpa=cgpa, backlogs=backlogs, attendance=attendance,
                internships=internships, projects=projects, certifications=certs,
                hackathons=hackathons, communication_score=communication, aptitude_score=aptitude,
                lms_activity=lms, skills=skills, mock_interview_scores=mock_scores,
                avg_mock_score=avg_mock, readiness_score=readiness)
            db.add(s); db.flush()

            if placed:
                company = random.choice(COMPANIES)
                salary = max(250000, int(np.random.normal(500000, 150000)))
                db.add(Placement(student_id=s.id, company_id=company_map[company].id,
                    role=random.choice(ROLES), salary=salary,
                    placement_date=datetime(2024,1,1)+timedelta(days=random.randint(0,300)),
                    is_internship_conversion=random.random()<0.2))
            created += 1

        db.commit()
        total = db.query(Student).count()
        placed_count = db.query(Placement).count()
        print(f"✅ Seeded: {created} students, {len(PROGRAMS)} programs, {len(COMPANIES)} companies")
        print(f"📊 Stats: {total} total students, {placed_count} placed ({placed_count/max(total,1)*100:.1f}%)")
        print("\n🚀 Next steps:")
        print("   Backend:   uvicorn placement_ai.api.main:app --reload --port 8000")
        print("   Streamlit: streamlit run app.py")

if __name__ == "__main__":
    seed()
