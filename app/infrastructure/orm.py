from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TaskORM(Base):
    __tablename__ = "tasks"

    file_id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_path: Mapped[str] = mapped_column(String, nullable=False)
    output_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str | None] = mapped_column(String)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
