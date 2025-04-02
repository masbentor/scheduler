from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Union, Optional, Any
from ..utils.exceptions import (
    GroupNotFoundException,
    PersonNotFoundException,
    InsufficientGroupMembersError,
    InvalidScheduleError
)
from ..utils.logging import logger
from ..config.settings import get_settings
from ..models.schemas import Group, Schedule, ScheduleEntry

class SchedulerService:
    """Service for managing groups and generating schedules"""
    
    def __init__(self):
        self._groups: Dict[str, List[str]] = {}
        self._schedule: Dict[str, Dict[str, str]] = {}
        self._settings = get_settings()
        self._person_constraints: Dict[str, Dict[str, Optional[int]]] = {}  # Store person constraints
    
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
            
        if person not in self._groups[group_id]:
            self._groups[group_id].append(person)
            logger.debug(f"Added {person} to group {group_id}")

    def bulk_add_groups(self, group_ids: List[Union[str, int]]) -> Dict[str, bool]:
        """Add multiple groups at once
        
        Args:
            group_ids: List of group IDs to add
            
        Returns:
            Dict mapping group_id to success status
        """
        logger.info(f"Bulk adding {len(group_ids)} groups")
        results = {}
        
        for group_id in group_ids:
            group_id = str(group_id)
            if group_id not in self._groups:
                self._groups[group_id] = []
                results[group_id] = True
                logger.debug(f"Created group {group_id}")
            else:
                results[group_id] = False
                logger.debug(f"Group {group_id} already exists")
                
        return results

    def bulk_add_people_to_groups(
        self, 
        assignments: Dict[str, List[Any]]
    ) -> Dict[str, List[str]]:
        """Add multiple people to multiple groups at once
        
        Args:
            assignments: Dictionary mapping group_ids to lists of people with constraints
            
        Returns:
            Dict mapping group_ids to lists of newly added people
        """
        logger.info(f"Bulk adding people to {len(assignments)} groups")
        results = {}
        
        for group_id, people in assignments.items():
            group_id = str(group_id)
            if group_id not in self._groups:
                self._groups[group_id] = []
                logger.debug(f"Created new group {group_id}")
            
            added_people = []
            for person in people:
                try:
                    # Extract person data
                    person_name = person.name
                    min_days = person.min_days
                    max_days = person.max_days
                    
                    if not person_name.strip():
                        logger.warning(f"Skipping empty person name for group {group_id}")
                        continue
                    
                    # Store constraints
                    self._person_constraints[person_name] = {
                        'min_days': min_days,
                        'max_days': max_days
                    }
                    
                    # Add to group if not already present
                    if person_name not in self._groups[group_id]:
                        self._groups[group_id].append(person_name)
                        added_people.append(person_name)
                        logger.debug(f"Added {person_name} to group {group_id}")
                except AttributeError as e:
                    logger.error(f"Invalid person data format in group {group_id}: {str(e)}")
                    raise ValueError(f"Invalid person data format in group {group_id}")
            
            if added_people:
                results[group_id] = added_people
                
        return results

    def remove_person_from_group(self, person: str, group_id: Union[str, int]) -> bool:
        """Remove a person from a group
        
        Args:
            person: Name of person to remove
            group_id: ID of group to remove from
            
        Returns:
            bool: True if person was removed
            
        Raises:
            GroupNotFoundException: If group doesn't exist
            PersonNotFoundException: If person not in group
        """
        group_id = str(group_id)
        logger.info(f"Removing {person} from group {group_id}")
        
        if group_id not in self._groups:
            raise GroupNotFoundException(f"Group {group_id} not found")
            
        if person not in self._groups[group_id]:
            raise PersonNotFoundException(f"Person {person} not found in group {group_id}")
            
        self._groups[group_id].remove(person)
        logger.debug(f"Removed {person} from group {group_id}")
        return True
    
    def delete_group(self, group_id: Union[str, int]) -> bool:
        """Delete an entire group
        
        Args:
            group_id: ID of group to delete
            
        Returns:
            bool: True if group was deleted
            
        Raises:
            GroupNotFoundException: If group doesn't exist
        """
        group_id = str(group_id)
        logger.info(f"Deleting group {group_id}")
        
        if group_id not in self._groups:
            raise GroupNotFoundException(f"Group {group_id} not found")
            
        del self._groups[group_id]
        logger.debug(f"Deleted group {group_id}")
        return True

    def generate_monthly_schedule(self, year: int, month: int) -> Schedule:
        """Generate a monthly schedule assigning one person from each group to each day
        
        Args:
            year: Year to generate schedule for
            month: Month to generate schedule for
            
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
        assignments_count: Dict[str, int] = {}  # Track number of assignments per person
        
        for day in range(1, num_days + 1):
            date = datetime(year, month, day).strftime("%Y-%m-%d")
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
                last_scheduled[chosen_person] = date
                assignments_count[chosen_person] = assignments_count.get(chosen_person, 0) + 1
            
            schedule[date] = day_schedule
            logger.debug(f"Generated schedule for {date}")

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

        self._schedule = schedule
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

    def get_schedule(self) -> Optional[Schedule]:
        """Get the current schedule
        
        Returns:
            Schedule object if exists, None otherwise
        """
        return Schedule(entries=self._schedule) if self._schedule else None

    def get_person_schedule(self, person: str) -> List[str]:
        """Get all dates when a person is scheduled
        
        Args:
            person: Name of person to get schedule for
            
        Returns:
            List of dates the person is scheduled
        """
        dates = []
        for date, assignments in self._schedule.items():
            if person in assignments.values():
                dates.append(date)
        return sorted(dates)
        
    def get_groups(self) -> Dict[str, Group]:
        """Get all groups and their members
        
        Returns:
            Dictionary mapping group IDs to Group objects
        """
        return {
            group_id: Group(id=group_id, members=members)
            for group_id, members in self._groups.items()
        } 