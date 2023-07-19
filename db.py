from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///wf.db"

# Connect to the database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite
    echo=True # Log generated SQL
)

def get_session():
    with Session(engine) as session:
        yield session