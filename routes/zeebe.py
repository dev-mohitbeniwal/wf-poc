from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from db import get_session
from models.report import Report
from zeebeClient import client

zeebeRouter = APIRouter(prefix="/api/zeebe")

@zeebeRouter.get('/report')
async def list_reports(session: Session = Depends(get_session)):
    query = select(Report)
    reports = session.exec(query).all()
    return reports

@zeebeRouter.get('/report/{id}')
async def get_report(id: int, session: Session = Depends(get_session)):
    query = select(Report).where(Report.id == id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Report with id {id} not found")
    return result

@zeebeRouter.post('/report')
async def initiate_report(report: Report, session: Session = Depends(get_session)):
    # Check if the approver exists or not
    query = select(User).where(User.username == report.approver)
    if not session.exec(query).first():
        raise HTTPException(status_code=400, detail="Invalid Approver")
    
    # Create a new report instance
    new_report = Report.from_orm(report)

    # Also initiate the report approval workflow
    process_instance_key = await client.run_process(report.zeebeProcessId, variables=getVariables(report))
    new_report.processInstanceKey = process_instance_key

    # Store the new report request in the db
    session.add(new_report)
    session.commit()
    session.refresh(new_report)
    return new_report


@zeebeRouter.put('/report')
async def update_report(username: str, password: str, reportId: int, session: Session = Depends(get_session)):
    # Check if the approver exists or not
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not (user and user.verify_password(password)):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    query = select(Report).where(Report.id == reportId)
    report = session.exec(query).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"No report with id: {reportId} found")
    
    


def getVariables(report: Report):
    return {
        "id": report.id,
        "name": report.name,
        "approver": report.approver,
        "requestor": report.requestor,
        "description": report.description,
        "status": report.status
    }