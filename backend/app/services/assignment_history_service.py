from datetime import date
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from statistics import stdev, StatisticsError
from app.models.assignment_history import AssignmentHistory, AssignmentStats
from app.models.assignment_history_db import AssignmentHistoryDB, DayType
from app.services.day_weight_service import DayWeightService

class AssignmentHistoryService:
    """Service for managing assignment history and fairness tracking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.weight_service = DayWeightService()
    
    def record_assignment(self, assignment: AssignmentHistory) -> AssignmentHistory:
        """Record a new assignment and update cumulative statistics"""
        # Get the latest record for this person in this group to get current stats
        latest = (
            self.db.query(AssignmentHistoryDB)
            .filter(
                AssignmentHistoryDB.person == assignment.person,
                AssignmentHistoryDB.group_id == assignment.group_id
            )
            .order_by(AssignmentHistoryDB.id.desc())
            .first()
        )
        
        # Calculate new cumulative stats
        cumulative_regular_days = (latest.cumulative_regular_days if latest else 0)
        cumulative_weighted_days = (latest.cumulative_weighted_days if latest else 0.0)
        cumulative_total_days = (latest.cumulative_total_days if latest else 0)
        
        # Calculate weight based on day type
        weight = self.weight_service.calculate_weight(
            target_date=assignment.assignment_date,
            day_type=assignment.day_type
        )
        
        # Update stats based on the new assignment
        if assignment.day_type == DayType.REGULAR:
            cumulative_regular_days += 1
        cumulative_weighted_days += weight
        cumulative_total_days += 1
        
        # Create new record
        db_assignment = AssignmentHistoryDB(
            person=assignment.person,
            group_id=assignment.group_id,
            date=assignment.assignment_date,
            day_type=assignment.day_type,
            weight=weight,
            cumulative_regular_days=cumulative_regular_days,
            cumulative_weighted_days=cumulative_weighted_days,
            cumulative_total_days=cumulative_total_days
        )
        
        self.db.add(db_assignment)
        self.db.commit()
        self.db.refresh(db_assignment)
        
        # Convert back to Pydantic model
        return AssignmentHistory(
            person=db_assignment.person,
            group_id=db_assignment.group_id,
            assignment_date=db_assignment.date,
            day_type=db_assignment.day_type,
            weight=db_assignment.weight,
            cumulative_regular_days=db_assignment.cumulative_regular_days,
            cumulative_weighted_days=db_assignment.cumulative_weighted_days,
            cumulative_total_days=db_assignment.cumulative_total_days
        )
    
    def get_person_stats(self, person: str, group_id: str) -> AssignmentStats:
        """Get assignment statistics for a specific person in a group"""
        stats = (
            self.db.query(
                func.count(AssignmentHistoryDB.id).label('total_assignments'),
                func.sum(AssignmentHistoryDB.weight).label('total_weighted_score'),
                func.sum(case((AssignmentHistoryDB.day_type == DayType.REGULAR, 1), else_=0)).label('regular_days'),
                func.sum(case((AssignmentHistoryDB.day_type == DayType.WEEKEND, 1), else_=0)).label('weekend_days'),
                func.sum(case((AssignmentHistoryDB.day_type == DayType.HOLIDAY, 1), else_=0)).label('holiday_days')
            )
            .filter(
                AssignmentHistoryDB.person == person,
                AssignmentHistoryDB.group_id == group_id
            )
            .first()
        )
        
        return AssignmentStats(
            total_assignments=stats[0] or 0,
            total_weighted_score=float(stats[1] or 0),
            regular_days=stats[2] or 0,
            weekend_days=stats[3] or 0,
            holiday_days=stats[4] or 0
        )
    
    def get_group_stats(self, group_id: str) -> Dict[str, AssignmentStats]:
        """Get assignment statistics for all people in a group"""
        people = (
            self.db.query(AssignmentHistoryDB.person)
            .filter(AssignmentHistoryDB.group_id == group_id)
            .distinct()
            .all()
        )
        
        return {
            person[0]: self.get_person_stats(person[0], group_id)
            for person in people
        }
    
    def get_fairness_metrics(self, group_id: str) -> Dict[str, float]:
        """Calculate fairness metrics for a group"""
        stats = self.get_group_stats(group_id)
        if not stats:
            return {
                "weighted_std_dev": 0.0,
                "max_weighted_diff": 0.0,
                "max_total_diff": 0
            }
            
        weighted_scores = [s.total_weighted_score for s in stats.values()]
        total_assignments = [s.total_assignments for s in stats.values()]
        
        # Calculate standard deviation of weighted scores
        mean_weighted = sum(weighted_scores) / len(weighted_scores)
        weighted_variance = sum((x - mean_weighted) ** 2 for x in weighted_scores) / len(weighted_scores)
        weighted_std_dev = weighted_variance ** 0.5
        
        # Calculate maximum differences
        max_weighted_diff = max(weighted_scores) - min(weighted_scores)
        max_total_diff = max(total_assignments) - min(total_assignments)
        
        return {
            "weighted_std_dev": weighted_std_dev,
            "max_weighted_diff": max_weighted_diff,
            "max_total_diff": max_total_diff
        } 