# Mocked API: Get team compensation and capex budget
def get_team_capex(uid):
    """Returns team capex and compensation details for manager"""
    return {
        "manager": uid,
        "team": "AI Team",
        "total_comp": 1500000,
        "bonus": 250000
    }
