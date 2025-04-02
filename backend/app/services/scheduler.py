from typing import Dict, List, Optional, Set, Union
from datetime import datetime, timedelta
from calendar import monthrange
from ..models.schemas import Person, Group, Schedule
from ..utils.exceptions import GroupNotFoundException, PersonNotFoundException, InsufficientGroupMembersError, InvalidScheduleError
from ..utils.logging import logger
import random

class SchedulerService:
    def __init__(self):
        self._groups: Dict[Union[str, int], Group] = {}
        self._current_schedule: Optional[Schedule] = None

    def add_group(self, group_id: Union[str, int]) -> bool:
        """Add a new group"""
        if group_id in self._groups:
            return False
        self._groups[group_id] = Group(id=group_id)
        return True

    def bulk_add_groups(self, group_ids: List[Union[str, int]]) -> Dict[Union[str, int], bool]:
        """Add multiple groups at once"""
        results = {}
        for group_id in group_ids:
            results[group_id] = self.add_group(group_id)
        return results

    def delete_group(self, group_id: Union[str, int]) -> None:
        """Delete a group"""
        if group_id not in self._groups:
            raise GroupNotFoundException(f"Group {group_id} not found")
        del self._groups[group_id]

    def add_person_to_group(
        self,
        name: str,
        group_id: Union[str, int],
        min_days: int = 1,
        max_days: int = 31
    ) -> None:
        """Add a person to a group"""
        if group_id not in self._groups:
            raise GroupNotFoundException(f"Group {group_id} not found")

        # Validate min_days and max_days
        if min_days < 0:
            raise ValueError("min_days cannot be negative")
        if max_days < min_days:
            raise ValueError("max_days cannot be less than min_days")
        if max_days < 1:
            raise ValueError("max_days must be at least 1")

        # Check if person already exists in the group
        group = self._groups[group_id]
        if any(member.name == name for member in group.members):
            raise ValueError(f"Person {name} already exists in group {group_id}")

        # Add person to group
        person = Person(name=name, min_days=min_days, max_days=max_days)
        group.members.append(person)

    def bulk_add_people_to_groups(
        self,
        assignments: Dict[Union[str, int], List[Person]]
    ) -> Dict[Union[str, int], List[str]]:
        """Add multiple people to multiple groups"""
        results: Dict[Union[str, int], List[str]] = {}
        
        for group_id, people in assignments.items():
            if group_id not in self._groups:
                raise ValueError(f"Group {group_id} not found")
            
            added_people = []
            for person in people:
                try:
                    self.add_person_to_group(
                        person.name,
                        group_id,
                        min_days=person.min_days,
                        max_days=person.max_days
                    )
                    added_people.append(person.name)
                except ValueError as e:
                    logger.warning(f"Failed to add {person.name} to group {group_id}: {str(e)}")
            
            results[group_id] = added_people
        
        return results

    def remove_person_from_group(self, name: str, group_id: Union[str, int]) -> None:
        """Remove a person from a group"""
        if group_id not in self._groups:
            raise GroupNotFoundException(f"Group {group_id} not found")

        group = self._groups[group_id]
        for i, member in enumerate(group.members):
            if member.name == name:
                group.members.pop(i)
                return

        raise PersonNotFoundException(f"Person {name} not found in group {group_id}")

    def get_groups(self) -> Dict[Union[str, int], Group]:
        """Get all groups"""
        return self._groups

    def get_schedule(self) -> Optional[Schedule]:
        """Get the current schedule"""
        return self._current_schedule

    def get_person_schedule(self, name: str) -> List[str]:
        """Get a person's schedule"""
        if not self._current_schedule:
            return []

        dates = []
        for date, names in self._current_schedule.assignments.items():
            if name in names:
                dates.append(date)
        return sorted(dates)

    def generate_monthly_schedule(self, year: int, month: int) -> Schedule:
        """Generate a monthly schedule"""
        # Validate input
        if not self._groups:
            raise InvalidScheduleError("No groups available for scheduling")

        # Get the number of days in the month
        _, num_days = monthrange(year, month)

        # Initialize schedule
        schedule = Schedule(
            year=year,
            month=month,
            assignments={},
            groups=self._groups
        )

        # Generate assignments for each day
        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            schedule.assignments[date_str] = []

            # Try to assign people from each group
            for group in self._groups.values():
                if not group.members:
                    continue

                # Filter eligible members
                eligible_members = [
                    member for member in group.members
                    if len(member.assigned_dates) < member.max_days
                ]

                if not eligible_members:
                    raise InsufficientGroupMembersError(
                        f"No eligible members available in group {group.id} for date {date_str}"
                    )

                # Select a random member
                selected_member = random.choice(eligible_members)
                schedule.assignments[date_str].append(selected_member.name)
                selected_member.assigned_dates.append(date_str)

        self._current_schedule = schedule
        return schedule