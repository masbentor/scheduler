class GroupNotFoundException(Exception):
    """Raised when a group is not found"""
    pass

class PersonNotFoundException(Exception):
    """Raised when a person is not found in a group"""
    pass

class InsufficientGroupMembersError(Exception):
    """Raised when there are not enough eligible members in a group for scheduling"""
    pass

class InvalidScheduleError(Exception):
    """Raised when a schedule cannot be generated due to invalid conditions"""
    pass