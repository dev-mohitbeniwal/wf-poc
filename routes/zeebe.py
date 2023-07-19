from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from db import get_session
from models.report import Report
from models.user import User
from zeebeClient import client
from utils.auth import get_current_user

zeebeRouter = APIRouter(prefix="/api/zeebe")

@zeebeRouter.get('/report')
async def list_reports(current_user: User = Depends(get_current_user),  session: Session = Depends(get_session)):
    query = select(Report)
    reports = session.exec(query).all()
    return reports

@zeebeRouter.get('/report/{id}')
async def get_report(id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    query = select(Report).where(Report.id == id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Report with id {id} not found")
    return result

@zeebeRouter.post('/report')
async def initiate_report(report: Report, current_user: User = Depends(get_current_user),  session: Session = Depends(get_session)):
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


@zeebeRouter.put('/report/{id}')
async def update_report(id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Check if the approver exists or not
    query = select(Report).where(Report.id == id)
    report = session.exec(query).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"No report with id: {id} found")
    
    


def getVariables(report: Report):
    return {
        "id": report.id,
        "name": report.name,
        "approver": report.approver,
        "requestor": report.requestor,
        "description": report.description,
        "status": report.status
    }