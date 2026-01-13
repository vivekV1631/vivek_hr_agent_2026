# Mocked API: Get leave balance from SuccessFactors
def get_leave_balance(uid):
    """Returns leave balance for a given user ID"""
    return {
        "uid": uid,
        "annual_leave": 12,
        "sick_leave": 6,
        "casual_leave": 4
    }
