from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TaskORM(Base):
    __tablename__ = "tasks"

    file_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    error = Column(Text, nullable=True)
    input_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)
    created_at = Column(String)
    attempts = Column(Integer, default=0)
