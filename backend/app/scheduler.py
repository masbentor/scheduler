from datetime import datetime, timedelta
import calendar
from typing import List, Dict, Optional, Any, Union, Set

class Scheduler:
    def __init__(self):
        self.groups = {}  # Dictionary to store groups and their members
        self.schedule = {}  # Dictionary to store the schedule

    def add_person_to_group(self, person: str, group_id: Union[str, int]):
        """Add a person to specified group"""
        # Convert group_id to string to ensure consistent handling
        group_id = str(group_id)
        
        # Create the group if it doesn't exist
        if group_id not in self.groups:
            self.groups[group_id] = []
            
        # Add person if not already in the group
        if person not in self.groups[group_id]:
            self.groups[group_id].append(person)

    def bulk_add_groups(self, group_ids: List[Union[str, int]]) -> Dict[str, bool]:
        """Add multiple groups at once
        
        Args:
            group_ids: List of group IDs to add
            
        Returns:
            Dict mapping group_id to success status
        """
        results = {}
        for group_id in group_ids:
            group_id = str(group_id)
            if group_id not in self.groups:
                self.groups[group_id] = []
                results[group_id] = True
            else:
                results[group_id] = False
        return results

    def bulk_add_people_to_groups(self, assignments: Dict[Union[str, int], List[str]]) -> Dict[str, List[str]]:
        """Add multiple people to multiple groups at once
        
        Args:
            assignments: Dictionary mapping group_ids to lists of people to add
            
        Returns:
            Dict mapping group_ids to lists of newly added people
        """
        results = {}
        for group_id, people in assignments.items():
            group_id = str(group_id)
            # Create group if it doesn't exist
            if group_id not in self.groups:
                self.groups[group_id] = []
            
            # Track newly added people for this group
            added_people = []
            for person in people:
                if person not in self.groups[group_id]:
                    self.groups[group_id].append(person)
                    added_people.append(person)
            
            if added_people:
                results[group_id] = added_people
                
        return results

    def remove_person_from_group(self, person: str, group_id: Union[str, int]) -> bool:
        """Remove a person from a group
        
        Returns:
            bool: True if person was removed, False if person or group not found
        """
        group_id = str(group_id)
        
        if group_id not in self.groups:
            return False
            
        if person not in self.groups[group_id]:
            return False
            
        self.groups[group_id].remove(person)
        return True
    
    def delete_group(self, group_id: Union[str, int]) -> bool:
        """Delete an entire group
        
        Returns:
            bool: True if group was deleted, False if group not found
        """
        group_id = str(group_id)
        
        if group_id not in self.groups:
            return False
            
        del self.groups[group_id]
        return True

    def generate_monthly_schedule(self, year: int, month: int) -> Dict[str, Dict[str, str]]:
        """Generate a monthly schedule assigning one person from each group to each day
        
        Rules:
        - One person from each group is scheduled for each day
        - No person can be scheduled for consecutive days
        """
        # Validate there is at least one group with one person
        if not self.groups:
            raise ValueError("No groups have been created")
            
        # Check if all groups have at least one person
        empty_groups = [group for group, members in self.groups.items() if not members]
        if empty_groups:
            raise ValueError(f"The following groups have no members: {empty_groups}")
            
        # Check if each group has enough people for the consecutive days rule
        for group_id, members in self.groups.items():
            if len(members) < 2:
                raise ValueError(f"Group {group_id} needs at least 2 people to avoid consecutive day assignments")

        # Get number of days in the month
        num_days = calendar.monthrange(year, month)[1]
        
        schedule = {}
        # Keep track of last scheduled date for each person
        last_scheduled = {}  # Format: {person_name: date_str}
        
        # Generate schedule for each day
        for day in range(1, num_days + 1):
            date = datetime(year, month, day).strftime("%Y-%m-%d")
            day_schedule = {}
            
            # Process each group
            for group_id, members in self.groups.items():
                # Find eligible people (not scheduled yesterday)
                eligible_members = []
                
                for person in members:
                    # Check if person was scheduled on the previous day
                    if (person not in last_scheduled or 
                        last_scheduled[person] != (datetime(year, month, day) - timedelta(days=1)).strftime("%Y-%m-%d")):
                        eligible_members.append(person)
                
                # If no eligible people (should rarely happen with proper validation), 
                # fall back to using anyone from the group
                if not eligible_members:
                    eligible_members = members
                
                # Choose the person who has been scheduled least recently
                chosen_person = None
                oldest_date = None
                
                for person in eligible_members:
                    if person not in last_scheduled:
                        # Person hasn't been scheduled yet, prioritize them
                        chosen_person = person
                        break
                    elif oldest_date is None or last_scheduled[person] < oldest_date:
                        oldest_date = last_scheduled[person]
                        chosen_person = person
                
                # If still no chosen person (shouldn't happen), pick the first eligible one
                if chosen_person is None and eligible_members:
                    chosen_person = eligible_members[0]
                
                # Assign the chosen person
                day_schedule[group_id] = chosen_person
                
                # Update the last scheduled date for this person
                last_scheduled[chosen_person] = date
            
            schedule[date] = day_schedule

        self.schedule = schedule
        return schedule

    def get_schedule(self) -> Dict[str, Dict[str, str]]:
        """Return the current schedule"""
        return self.schedule

    def get_person_schedule(self, person: str) -> List[str]:
        """Get all dates when a person is scheduled"""
        dates = []
        for date, assignments in self.schedule.items():
            if person in assignments.values():
                dates.append(date)
        return sorted(dates)
        
    def get_groups(self) -> Dict[str, List[str]]:
        """Return all groups and their members"""
        return self.groups 