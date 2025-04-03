from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..config.database import Base

class Person(Base):
    __tablename__ = "people"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    min_days = Column(Integer, nullable=True)
    max_days = Column(Integer, nullable=True)

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(String, ForeignKey("groups.id"), nullable=False)
    person_id = Column(String, ForeignKey("people.id"), nullable=False)

    # Relationships
    group = relationship("Group", backref="members")
    person = relationship("Person", backref="group_memberships") 