"""FastAPI Backend — Placement AI Platform"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import os

from placement_ai.utils.database import get_db, init_db
from placement_ai.utils.models import Student, SkillProgram, Company, Placement, IndustryRequirement
from placement_ai.utils.config import settings

app = FastAPI(title="Placement AI Platform", version="1.0.0",
    description="Multi-Agentic AI + RAG + Placement Intelligence Ecosystem")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/", tags=["System"])
async def root():
    return {"message": "Placement AI Platform", "status": "running", "version": "1.0.0"}

@app.get("/health", tags=["System"])
async def health():
    return {"status": "healthy", "groq_model": settings.LLM_MODEL}

@app.get("/api/students", tags=["Students"])
async def get_students(skip: int=0, limit: int=500, department: Optional[str]=None,
    batch: Optional[int]=None, db: AsyncSession=Depends(get_db)):
    q = select(Student)
    if department: q = q.where(Student.department == department)
    if batch: q = q.where(Student.batch == batch)
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    students = result.scalars().all()
    return [{"id":s.id,"student_id":s.student_id,"name":s.name,"email":s.email,
             "department":s.department,"batch":s.batch,"cgpa":s.cgpa,"backlogs":s.backlogs,
             "internships":s.internships,"projects":s.projects,"certifications":s.certifications,
             "hackathons":s.hackathons,"communication_score":s.communication_score,
             "aptitude_score":s.aptitude_score,"attendance":s.attendance,"lms_activity":s.lms_activity,
             "skills":s.skills,"mock_interview_scores":s.mock_interview_scores,
             "avg_mock_score":s.avg_mock_score,"readiness_score":s.readiness_score} for s in students]

@app.get("/api/students/{student_id}", tags=["Students"])
async def get_student(student_id: int, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == student_id))
    s = result.scalar_one_or_none()
    if not s: raise HTTPException(404, "Student not found")
    return {"id":s.id,"student_id":s.student_id,"name":s.name,"department":s.department,
            "batch":s.batch,"cgpa":s.cgpa,"backlogs":s.backlogs,"internships":s.internships,
            "projects":s.projects,"certifications":s.certifications,"hackathons":s.hackathons,
            "communication_score":s.communication_score,"aptitude_score":s.aptitude_score,
            "attendance":s.attendance,"lms_activity":s.lms_activity,"skills":s.skills,
            "mock_interview_scores":s.mock_interview_scores,"avg_mock_score":s.avg_mock_score,
            "readiness_score":s.readiness_score}

@app.get("/api/analytics/overview", tags=["Analytics"])
async def get_overview(db: AsyncSession=Depends(get_db)):
    total = (await db.execute(select(func.count(Student.id)))).scalar()
    placed = (await db.execute(select(func.count(Placement.id)))).scalar()
    avg_ctc = (await db.execute(select(func.avg(Placement.salary)))).scalar() or 0
    avg_cgpa = (await db.execute(select(func.avg(Student.cgpa)))).scalar() or 0
    avg_readiness = (await db.execute(select(func.avg(Student.readiness_score)))).scalar() or 0
    return {"total_students":total,"placed_students":placed,
            "placement_rate":round(placed/max(total,1)*100,1),
            "avg_ctc":round(avg_ctc),"avg_cgpa":round(avg_cgpa,2),
            "avg_readiness":round(avg_readiness,1)}

@app.get("/api/analytics/departments", tags=["Analytics"])
async def get_departments(db: AsyncSession=Depends(get_db)):
    result = await db.execute(
        select(Student.department, func.count(Student.id), func.avg(Student.cgpa), func.avg(Student.readiness_score))
        .group_by(Student.department))
    rows = result.all()
    return [{"department":r[0],"count":r[1],"avg_cgpa":round(r[2],2),"avg_readiness":round(r[3],1)} for r in rows]

@app.get("/api/analytics/programs", tags=["Analytics"])
async def get_programs(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(SkillProgram))
    programs = result.scalars().all()
    return [{"id":p.id,"program_id":p.program_id,"name":p.name,"duration_weeks":p.duration_weeks,
             "hours":p.hours,"cost":p.cost,"skills_covered":p.skills_covered,
             "completion_rate":p.completion_rate,"avg_feedback_score":p.avg_feedback_score,
             "industry_relevance":p.industry_relevance} for p in programs]

@app.get("/api/companies", tags=["Companies"])
async def get_companies(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Company))
    companies = result.scalars().all()
    return [{"id":c.id,"name":c.name,"tier":c.tier,"required_skills":c.required_skills,
             "avg_package":c.avg_package,"hiring_trend":c.hiring_trend} for c in companies]

@app.get("/api/placements", tags=["Placements"])
async def get_placements(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Placement, Student, Company)
        .join(Student, Placement.student_id==Student.id)
        .join(Company, Placement.company_id==Company.id).limit(500))
    rows = result.all()
    return [{"id":p.id,"student_name":s.name,"student_id":s.student_id,
             "company":c.name,"role":p.role,"salary":p.salary,
             "placement_date":str(p.placement_date)} for p,s,c in rows]

@app.post("/api/agents/student-intelligence/{student_id}", tags=["Agents"])
async def run_student_intelligence(student_id: int, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id==student_id))
    s = result.scalar_one_or_none()
    if not s: raise HTTPException(404, "Student not found")
    from placement_ai.agents.crew import agent_student_intelligence
    student_dict = {"name":s.name,"cgpa":s.cgpa,"skills":s.skills,"backlogs":s.backlogs,
                    "internships":s.internships,"projects":s.projects,
                    "communication_score":s.communication_score,"avg_mock_score":s.avg_mock_score}
    return agent_student_intelligence(student_dict)

@app.get("/api/agents/program-impact", tags=["Agents"])
async def run_program_impact(db: AsyncSession=Depends(get_db)):
    programs_r = await db.execute(select(SkillProgram))
    placements_r = await db.execute(select(Placement))
    programs = [{"name":p.name,"cost":p.cost,"has_internship":p.has_internship} for p in programs_r.scalars().all()]
    placements = [{"salary":p.salary} for p in placements_r.scalars().all()]
    from placement_ai.agents.crew import agent_skill_program_impact
    return agent_skill_program_impact(programs, placements)

@app.get("/api/agents/salary-intelligence", tags=["Agents"])
async def run_salary_intelligence(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Placement))
    placements = [{"salary":p.salary} for p in result.scalars().all()]
    from placement_ai.agents.crew import agent_salary_intelligence
    return agent_salary_intelligence(placements)

@app.get("/api/agents/benchmarking", tags=["Agents"])
async def run_benchmarking(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Student).limit(200))
    students = [{"department":s.department,"batch":s.batch,"readiness_score":s.readiness_score} for s in result.scalars().all()]
    from placement_ai.agents.crew import agent_benchmarking
    return agent_benchmarking(students)

@app.get("/api/agents/recruiter-intelligence", tags=["Agents"])
async def run_recruiter_intelligence(db: AsyncSession=Depends(get_db)):
    companies_r = await db.execute(select(Company))
    placements_r = await db.execute(select(Placement))
    companies = [{"name":c.name,"tier":c.tier,"required_skills":c.required_skills,"avg_package":c.avg_package,"hiring_trend":c.hiring_trend} for c in companies_r.scalars().all()]
    placements = [{"salary":p.salary} for p in placements_r.scalars().all()]
    from placement_ai.agents.crew import agent_recruiter_intelligence
    return agent_recruiter_intelligence(companies, placements)

@app.get("/api/agents/intervention/{student_id}", tags=["Agents"])
async def run_intervention(student_id: int, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id==student_id))
    s = result.scalar_one_or_none()
    if not s: raise HTTPException(404, "Student not found")
    from placement_ai.agents.crew import agent_intervention
    return agent_intervention({"readiness_score":s.readiness_score,"backlogs":s.backlogs,
                                "skills":s.skills,"avg_mock_score":s.avg_mock_score})

@app.get("/api/agents/curriculum-optimization", tags=["Agents"])
async def run_curriculum(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(SkillProgram))
    programs = [{"name":p.name,"skills_covered":p.skills_covered} for p in result.scalars().all()]
    from placement_ai.agents.crew import agent_curriculum_optimization
    return agent_curriculum_optimization(programs, {})

@app.post("/api/agents/skill-gap", tags=["Agents"])
async def run_skill_gap(data: dict, db: AsyncSession=Depends(get_db)):
    from placement_ai.agents.crew import agent_skill_gap
    return agent_skill_gap(data.get("skills",[]), data.get("target_role","Software Engineer"))

@app.post("/api/chatbot/ask", tags=["Chatbot"])
async def ask_chatbot(data: dict, db: AsyncSession=Depends(get_db)):
    question = data.get("question","")
    if not question: raise HTTPException(400,"Question required")
    from placement_ai.rag.pipeline import query_rag
    answer = query_rag(question)
    return {"question":question,"answer":answer,"sources":["Placement Records","Student Profiles","Skill Programs"]}

@app.post("/api/ml/train", tags=["ML"])
async def train_models(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Student, Placement)
        .outerjoin(Placement, Student.id==Placement.student_id))
    rows = result.all()
    students = []
    for s, p in rows:
        students.append({
            "cgpa":s.cgpa,"backlogs":s.backlogs,"internships":s.internships,
            "projects":s.projects,"certifications":s.certifications,
            "avg_mock_score":s.avg_mock_score,"skills":s.skills,
            "batch":s.batch,"communication_score":s.communication_score,
            "aptitude_score":s.aptitude_score,"attendance":s.attendance,
            "lms_activity":s.lms_activity,"department":s.department,
            "placed": p is not None
        })
    from placement_ai.prediction.pipeline import get_predictor
    predictor = get_predictor()
    result_data = predictor.train(students)
    result_data["message"] = f"Training complete on {len(students)} students"
    return result_data

@app.get("/api/ml/predict/{student_id}", tags=["ML"])
async def predict_placement(student_id: int, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id==student_id))
    s = result.scalar_one_or_none()
    if not s: raise HTTPException(404, "Student not found")
    p_result = await db.execute(select(Placement).where(Placement.student_id==student_id))
    is_placed = p_result.scalar_one_or_none() is not None
    from placement_ai.prediction.pipeline import get_predictor
    predictor = get_predictor()
    if not predictor.is_trained:
        from placement_ai.agents.crew import agent_placement_prediction
        student_dict = {"cgpa":s.cgpa,"backlogs":s.backlogs,"internships":s.internships,
                        "projects":s.projects,"skills":s.skills,"avg_mock_score":s.avg_mock_score}
        return agent_placement_prediction(student_dict)
    student_dict = {"cgpa":s.cgpa,"backlogs":s.backlogs,"internships":s.internships,
                    "projects":s.projects,"certifications":s.certifications,
                    "avg_mock_score":s.avg_mock_score,"skills":s.skills,
                    "batch":s.batch,"communication_score":s.communication_score,
                    "aptitude_score":s.aptitude_score,"attendance":s.attendance,
                    "lms_activity":s.lms_activity,"department":s.department}
    result_data = predictor.predict(student_dict)
    result_data["student_name"] = s.name
    result_data["actual_placed"] = is_placed
    return result_data

@app.get("/api/ml/forecast", tags=["ML"])
async def forecast_placements(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Placement))
    placements = [{"placement_date":str(p.placement_date),"salary":p.salary} for p in result.scalars().all()]
    from placement_ai.prediction.pipeline import get_forecaster
    return get_forecaster().forecast(placements, periods=6)
