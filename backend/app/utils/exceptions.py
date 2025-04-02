class SchedulerException(Exception):
    """Base exception for scheduler errors"""
    pass

class GroupNotFoundException(SchedulerException):
    """Raised when a group is not found"""
    pass

class PersonNotFoundException(SchedulerException):
    """Raised when a person is not found"""
    pass

class InsufficientGroupMembersError(SchedulerException):
    """Raised when a group doesn't have enough members"""
    pass

class InvalidScheduleError(SchedulerException):
    """Raised when schedule generation fails"""
    pass

class DuplicateAssignmentError(SchedulerException):
    """Raised when trying to assign a person who is already assigned"""
    pass 