from datetime import datetime, date, timedelta
from typing import Dict, List, Union, Optional, Any, Set
import calendar
import logging
from sqlalchemy.orm import Session
from sqlalchemy import extract
from ..utils.exceptions import (
    GroupNotFoundException,
    PersonNotFoundException,
    InsufficientGroupMembersError,
    InvalidScheduleError
)
from ..utils.logging import logger
from ..config.settings import get_settings
from ..models.schemas import Group, Schedule, ScheduleEntry
from ..models.assignment_history import AssignmentHistory
from ..models.assignment_history_db import DayType, AssignmentHistoryDB
from ..services.assignment_history_service import AssignmentHistoryService
from ..services.day_weight_service import DayWeightService
from ..models.holiday import Holiday
import traceback
from ..models.group import Group
from ..models.person import Person, GroupMember
from ..models.request import PersonAssignment

class SchedulerService:
    """Service for managing groups and generating schedules"""
    
    def __init__(self, db: Session):
        self._groups: Dict[str, List[str]] = {}
        self._person_constraints: Dict[str, Dict[str, Optional[int]]] = {}
        self._settings = get_settings()
        self.db = db
        self.assignment_history = AssignmentHistoryService(db)
        self.day_weight_service = DayWeightService()
        self._load_from_database()  # Load data from database
    
    def _load_from_database(self) -> None:
        """Load groups and their members from the database"""
        try:
            # Load all groups
            db_groups = self.db.query(Group).all()
            for group in db_groups:
                self._groups[group.id] = []
                
            # Load all group members and their constraints
            group_members = (
                self.db.query(GroupMember, Person)
                .join(Person, GroupMember.person_id == Person.id)
                .all()
            )
            
            for membership, person in group_members:
                group_id = membership.group_id
                name = person.name
                
                # Add to groups
                if name not in self._groups[group_id]:
                    self._groups[group_id].append(name)
                
                # Store constraints
                if person.min_days is not None or person.max_days is not None:
                    self._person_constraints[name] = {
                        'min_days': person.min_days,
                        'max_days': person.max_days
                    }
                    
            logger.debug(f"Loaded groups from database: {self._groups}")
            logger.debug(f"Loaded constraints from database: {self._person_constraints}")
            
        except Exception as e:
            logger.error(f"Error loading from database: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def add_person_to_group(self, person: str, group_id: Union[str, int], min_days: Optional[int] = None, max_days: Optional[int] = None) -> None:
        """Add a person to specified group
        
        Args:
            person: Name of the person to add
            group_id: ID of the group to add to
            min_days: Minimum days to schedule per month
            max_days: Maximum days to schedule per month
            
        Raises:
            ValueError: If person name is empty or constraints are invalid
        """
        if not person.strip():
            raise ValueError("Person name cannot be empty")
            
        if min_days is not None and max_days is not None and min_days > max_days:
            raise ValueError("min_days cannot be greater than max_days")
            
        group_id = str(group_id)
        logger.info(f"Adding person {person} to group {group_id}")
        
        # Store person constraints
        self._person_constraints[person] = {
            'min_days': min_days,
            'max_days': max_days
        }
        
        if group_id not in self._groups:
            self._groups[group_id] = []
            logger.debug(f"Created new group {group_id}")
            
        # Add person if not already in the group
        if person not in self._groups[group_id]:
            self._groups[group_id].append(person)

    def bulk_add_groups(self, group_ids: List[str]) -> bool:
        """Add multiple groups at once
        
        Args:
            group_ids: List of group IDs to create
            
        Returns:
            bool: True if all groups were created successfully
        """
        try:
            logger.debug(f"Creating groups: {group_ids}")
            for group_id in group_ids:
                # Create group in memory
                if group_id not in self._groups:
                    self._groups[group_id] = []
                    logger.debug(f"Created group in memory: {group_id}")
                else:
                    logger.debug(f"Group already exists in memory: {group_id}")
                
                # Create group in database if it doesn't exist
                db_group = self.db.query(Group).filter(Group.id == group_id).first()
                if not db_group:
                    db_group = Group(id=group_id)
                    self.db.add(db_group)
                    logger.debug(f"Created group in database: {group_id}")
            
            # No explicit commit - handled by dependency
            return True
        except Exception as e:
            logger.error(f"Error creating groups: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def bulk_add_people_to_groups(
        self,
        assignments: Dict[str, List[PersonAssignment]]
    ) -> bool:
        """Add multiple people to groups with their constraints
        
        Args:
            assignments: Dictionary mapping group IDs to lists of person assignments
            
        Returns:
            bool: True if all people were added successfully
            
        Raises:
            GroupNotFoundException: If a specified group doesn't exist
            ValueError: If person data is invalid
        """
        try:
            logger.debug(f"Processing bulk people assignments: {assignments}")
            
            for group_id, people in assignments.items():
                # Check if group exists in database
                db_group = self.db.query(Group).filter(Group.id == group_id).first()
                if not db_group:
                    logger.error(f"Group not found: {group_id}")
                    raise GroupNotFoundException(f"Group {group_id} not found")
                
                # Update memory state
                if group_id not in self._groups:
                    self._groups[group_id] = []
                
                for person in people:
                    name = person.name
                    min_days = person.min_days
                    max_days = person.max_days
                    
                    # Store constraints in memory
                    if min_days is not None or max_days is not None:
                        self._person_constraints[name] = {
                            'min_days': min_days,
                            'max_days': max_days
                        }
                        logger.debug(f"Added constraints for {name}: min={min_days}, max={max_days}")
                    
                    # Create or update person in database
                    db_person = self.db.query(Person).filter(Person.name == name).first()
                    if not db_person:
                        db_person = Person(
                            id=name,  # Using name as ID for simplicity
                            name=name,
                            min_days=min_days,
                            max_days=max_days
                        )
                        self.db.add(db_person)
                        logger.debug(f"Created person in database: {name}")
                    else:
                        db_person.min_days = min_days
                        db_person.max_days = max_days
                        logger.debug(f"Updated person in database: {name}")
                    
                    # Add group membership in database
                    db_membership = (
                        self.db.query(GroupMember)
                        .filter(
                            GroupMember.group_id == group_id,
                            GroupMember.person_id == name
                        )
                        .first()
                    )
                    if not db_membership:
                        db_membership = GroupMember(
                            group_id=group_id,
                            person_id=name
                        )
                        self.db.add(db_membership)
                        logger.debug(f"Added {name} to group {group_id} in database")
                    
                    # Update memory state
                    if name not in self._groups[group_id]:
                        self._groups[group_id].append(name)
                        logger.debug(f"Added {name} to group {group_id} in memory")
            
            # Commit all changes
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error processing people assignments: {str(e)}")
            logger.error(traceback.format_exc())
            self.db.rollback()
            raise

    def remove_person_from_group(self, person: str, group_id: Union[str, int]) -> bool:
        """Remove a person from a group
        
        Args:
            person: Name of person to remove
            group_id: ID of group to remove from
            
        Returns:
            bool: True if person was removed, False if person or group not found
        """
        group_id = str(group_id)
        
        if group_id not in self._groups:
            return False
            
        if person not in self._groups[group_id]:
            return False
            
        self._groups[group_id].remove(person)
        if person in self._person_constraints:
            del self._person_constraints[person]
        return True
    
    def delete_group(self, group_id: Union[str, int]) -> bool:
        """Delete an entire group
        
        Args:
            group_id: ID of group to delete
            
        Returns:
            bool: True if group was deleted, False if group not found
        """
        group_id = str(group_id)
        
        if group_id not in self._groups:
            return False
            
        # Remove constraints for all people in the group
        for person in self._groups[group_id]:
            if person in self._person_constraints:
                del self._person_constraints[person]
                
        del self._groups[group_id]
        return True

    def generate_monthly_schedule(self, year: int, month: int, holidays: List[Holiday] = None) -> Schedule:
        """Generate a monthly schedule assigning one person from each group to each day
        
        Args:
            year: Year to generate schedule for
            month: Month to generate schedule for
            holidays: Optional list of holidays to consider for day type determination
            
        Returns:
            Schedule object with assignments
            
        Raises:
            InvalidScheduleError: If schedule cannot be generated
            InsufficientGroupMembersError: If groups don't have enough members
        """
        logger.info(f"Generating schedule for {year}-{month}")
        
        if not self._groups:
            raise InvalidScheduleError("No groups have been created")
            
        # Validate group members
        empty_groups = [group for group, members in self._groups.items() if not members]
        if empty_groups:
            raise InsufficientGroupMembersError(
                f"The following groups have no members: {empty_groups}"
            )
            
        for group_id, members in self._groups.items():
            if len(members) < self._settings.min_group_members:
                raise InsufficientGroupMembersError(
                    f"Group {group_id} needs at least {self._settings.min_group_members} "
                    "people to avoid consecutive day assignments"
                )

        num_days = calendar.monthrange(year, month)[1]
        schedule = {}
        last_scheduled: Dict[str, str] = {}
        assignments_count: Dict[str, int] = {}
        
        for day in range(1, num_days + 1):
            date_obj = datetime(year, month, day).date()
            date_str = date_obj.strftime("%Y-%m-%d")
            day_schedule = {}
            
            for group_id, members in self._groups.items():
                eligible_members = [
                    person for person in members
                    if (
                        # Not scheduled yesterday
                        (person not in last_scheduled or 
                        last_scheduled[person] != 
                        (datetime(year, month, day) - timedelta(days=1)).strftime("%Y-%m-%d"))
                        and
                        # Within max_days constraint if set
                        (person not in self._person_constraints 
                         or self._person_constraints[person]['max_days'] is None 
                         or assignments_count.get(person, 0) < self._person_constraints[person]['max_days'])
                    )
                ]
                
                if not eligible_members:
                    eligible_members = members
                
                chosen_person = self._select_person(eligible_members, last_scheduled, assignments_count)
                day_schedule[group_id] = chosen_person
                last_scheduled[chosen_person] = date_str
                assignments_count[chosen_person] = assignments_count.get(chosen_person, 0) + 1
                
                # Record assignment in history
                day_type = self.day_weight_service.get_day_type(date_obj, holidays)
                assignment = AssignmentHistory(
                    person=chosen_person,
                    group_id=group_id,
                    assignment_date=date_obj,
                    day_type=day_type,
                    weight=self.day_weight_service.calculate_weight(date_obj, day_type),
                    cumulative_regular_days=0,  # Will be calculated by service
                    cumulative_weighted_days=0.0,
                    cumulative_total_days=0
                )
                self.assignment_history.record_assignment(assignment)
            
            schedule[date_str] = day_schedule
            logger.debug(f"Generated schedule for {date_str}")

        # Validate minimum days constraints
        for person, constraints in self._person_constraints.items():
            min_days = constraints.get('min_days')
            if min_days is not None:
                actual_days = assignments_count.get(person, 0)
                if actual_days < min_days:
                    raise InvalidScheduleError(
                        f"Could not meet minimum days requirement for {person}. "
                        f"Required: {min_days}, Scheduled: {actual_days}"
                    )

        return Schedule(entries=schedule)

    def _select_person(
        self, 
        eligible_members: List[str],
        last_scheduled: Dict[str, str],
        assignments_count: Dict[str, int]
    ) -> str:
        """Select the most appropriate person from eligible members
        
        Args:
            eligible_members: List of eligible people
            last_scheduled: Dict mapping people to their last scheduled date
            assignments_count: Dict tracking number of assignments per person
            
        Returns:
            Selected person's name
        """
        # First try to satisfy minimum days constraints
        min_day_candidates = [
            p for p in eligible_members 
            if p in self._person_constraints 
            and self._person_constraints[p]['min_days'] is not None 
            and assignments_count.get(p, 0) < self._person_constraints[p]['min_days']
        ]
        
        if min_day_candidates:
            never_scheduled = [p for p in min_day_candidates if p not in last_scheduled]
            if never_scheduled:
                return never_scheduled[0]
            return min(
                min_day_candidates,
                key=lambda p: last_scheduled.get(p, "0000-00-00")
            )
            
        # If no minimum day constraints to satisfy, proceed with regular selection
        never_scheduled = [p for p in eligible_members if p not in last_scheduled]
        if never_scheduled:
            return never_scheduled[0]
            
        return min(
            eligible_members,
            key=lambda p: last_scheduled.get(p, "0000-00-00")
        )

    def get_schedule(self, year: Optional[int] = None, month: Optional[int] = None) -> Optional[Schedule]:
        """Get schedule from database
        
        Args:
            year: Optional year to filter by
            month: Optional month to filter by
            
        Returns:
            Schedule object if exists, None otherwise
        """
        # Query assignments from database
        query = self.db.query(AssignmentHistoryDB)
        
        if year is not None:
            query = query.filter(extract('year', AssignmentHistoryDB.date) == year)
        if month is not None:
            query = query.filter(extract('month', AssignmentHistoryDB.date) == month)
            
        assignments = query.order_by(AssignmentHistoryDB.date).all()
        
        if not assignments:
            return None
            
        # Convert to schedule format
        schedule = {}
        for assignment in assignments:
            date_str = assignment.date.strftime("%Y-%m-%d")
            if date_str not in schedule:
                schedule[date_str] = {}
            schedule[date_str][assignment.group_id] = assignment.person
            
        return Schedule(entries=schedule)

    def get_person_schedule(self, person: str, year: Optional[int] = None, month: Optional[int] = None) -> List[str]:
        """Get all dates when a person is scheduled
        
        Args:
            person: Name of person to get schedule for
            year: Optional year to filter by
            month: Optional month to filter by
            
        Returns:
            List of dates the person is scheduled
        """
        # Query assignments from database
        query = self.db.query(AssignmentHistoryDB).filter(AssignmentHistoryDB.person == person)
        
        if year is not None:
            query = query.filter(extract('year', AssignmentHistoryDB.date) == year)
        if month is not None:
            query = query.filter(extract('month', AssignmentHistoryDB.date) == month)
            
        assignments = query.order_by(AssignmentHistoryDB.date).all()
        return [assignment.date.strftime("%Y-%m-%d") for assignment in assignments]
        
    def get_groups(self) -> Dict[str, Group]:
        """Get all groups and their members
        
        Returns:
            Dictionary mapping group IDs to Group objects
        """
        return {
            group_id: Group(id=group_id, members=members)
            for group_id, members in self._groups.items()
        } 