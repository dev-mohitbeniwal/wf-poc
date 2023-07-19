from sqlmodel import SQLModel, Field
from passlib.context import CryptContext

class Report(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    requestor: str = None
    approver: str
    name: str
    description: str
    status: int = 0
    zeebeProcessId: str
    processInstanceKey: int = None