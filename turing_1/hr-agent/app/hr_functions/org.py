"""Organization - Organizational Structure and Team Members"""

def get_org_members(uid):
    """Get organization members / direct reports for a manager (mocked data)"""
    # Return manager ID and list of direct reports
    return {
        "manager": uid,             # Manager ID
        "members": ["emp101", "emp102", "emp103"]  # Direct reports
    }
