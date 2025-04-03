from sqlalchemy import Column, String
from ..config.database import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True)
    name = Column(String) 