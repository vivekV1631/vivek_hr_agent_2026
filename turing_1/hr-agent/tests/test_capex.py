"""
Unit Tests for Team Capex Module

This test module validates the team capex (budget and compensation) functionality.
It ensures that the get_team_capex function:
- Returns correct structure
- Contains all required budget fields
- Has reasonable financial values
- Maintains data consistency

Test Framework: pytest
Running tests: pytest tests/test_capex.py -v

Author: HR Agent Development Team
"""

from app.hr_functions.capex import get_team_capex


def test_team_capex_structure():
    """
    Test get_team_capex returns proper structure with all required fields.
    
    This test validates the API contract - ensuring the response contains
    all fields that dependent services expect.
    
    Test Data:
    - Input: "emp001" (manager UID)
    
    Assertions:
    - Response is a dictionary
    - Contains required fields: manager, team, total_comp, bonus
    - Manager UID is passed through correctly
    
    How to Run:
        pytest tests/test_capex.py::test_team_capex_structure -v
    
    Expected Result:
        test_team_capex_structure PASSED
    """
    # Call function with test manager UID
    data = get_team_capex("emp001")
    
    # Verify response type
    assert isinstance(data, dict), "Response should be a dictionary"
    
    # Verify all required fields are present
    required_fields = ["manager", "team", "total_comp", "bonus"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Verify manager UID is passed through
    assert data["manager"] == "emp001", "Manager UID not passed through correctly"
    
    # Verify team name exists
    assert isinstance(data["team"], str), "Team name should be a string"
    assert len(data["team"]) > 0, "Team name should not be empty"


def test_team_capex_values():
    """
    Test get_team_capex returns reasonable financial values.
    
    This test validates the budget numbers are sensible and realistic
    for a typical team in a technology company.
    
    Test Data:
    - Input: "emp002" (another manager UID)
    
    Assertions:
    - total_comp is a positive integer
    - bonus is a positive integer
    - bonus is less than total_comp (logical constraint)
    - Values are in reasonable range for team budget
    
    How to Run:
        pytest tests/test_capex.py::test_team_capex_values -v
    
    Expected Result:
        test_team_capex_values PASSED
    """
    # Call function with different manager UID
    data = get_team_capex("emp002")
    
    # Verify financial values are positive integers
    assert isinstance(data["total_comp"], int), "total_comp should be integer"
    assert data["total_comp"] > 0, "total_comp should be positive"
    
    assert isinstance(data["bonus"], int), "bonus should be integer"
    assert data["bonus"] > 0, "bonus should be positive"
    
    # Verify logical constraint: bonus cannot exceed total compensation
    assert data["bonus"] < data["total_comp"], \
        "Bonus pool should not exceed total compensation"
    
    # Verify values are in realistic range
    # Reasonable range: $500K - $5M for team annual budget
    assert data["total_comp"] >= 500000, "Team budget seems unreasonably low"
    assert data["total_comp"] <= 5000000, "Team budget seems unreasonably high"


def test_team_capex_bonus_ratio():
    """
    Test get_team_capex maintains reasonable bonus-to-comp ratio.
    
    This test validates business logic: bonus pool should be a reasonable
    percentage of total compensation (typically 10-30% for tech teams).
    
    Test Data:
    - Input: "emp003" (manager UID)
    
    Assertions:
    - Bonus is 10-30% of total compensation
    - Ratio is consistent and realistic
    
    How to Run:
        pytest tests/test_capex.py::test_team_capex_bonus_ratio -v
    
    Expected Result:
        test_team_capex_bonus_ratio PASSED
    """
    # Call function
    data = get_team_capex("emp003")
    
    # Calculate bonus as percentage of total compensation
    bonus_ratio = data["bonus"] / data["total_comp"]
    
    # Verify bonus ratio is between 10% and 30%
    assert 0.10 <= bonus_ratio <= 0.30, \
        f"Bonus ratio {bonus_ratio:.1%} outside expected range (10-30%)"
    
    # Additional check: typical tech company ratio should be around 15-20%
    # This is informational, not a hard assertion
    if bonus_ratio < 0.10:
        print(f"Warning: Bonus ratio {bonus_ratio:.1%} is low")
    if bonus_ratio > 0.30:
        print(f"Warning: Bonus ratio {bonus_ratio:.1%} is high")
