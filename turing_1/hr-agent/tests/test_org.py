"""
Unit Tests for Organization Module

This test module validates the organization structure and team composition functionality.
It ensures that the get_org_members function:
- Returns correct organizational structure
- Contains all required fields
- Returns valid employee IDs
- Maintains data consistency

Test Framework: pytest
Running tests: pytest tests/test_org.py -v

Author: HR Agent Development Team
"""

from app.hr_functions.org import get_org_members


def test_org_members_structure():
    """
    Test get_org_members returns proper organizational structure.
    
    This test validates the API contract and ensures the response
    contains all fields needed for org chart visualization.
    
    Test Data:
    - Input: "mgr001" (manager UID)
    
    Assertions:
    - Response is a dictionary
    - Contains required fields: manager, members
    - Manager UID is passed through correctly
    
    How to Run:
        pytest tests/test_org.py::test_org_members_structure -v
    
    Expected Result:
        test_org_members_structure PASSED
    """
    # Call function with test manager UID
    data = get_org_members("mgr001")
    
    # Verify response type
    assert isinstance(data, dict), "Response should be a dictionary"
    
    # Verify all required fields are present
    required_fields = ["manager", "members"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Verify manager UID is passed through
    assert data["manager"] == "mgr001", "Manager UID not passed through correctly"


def test_org_members_list():
    """
    Test get_org_members returns valid list of employees.
    
    This test validates that:
    - members field is a list
    - List contains valid employee IDs
    - List is not empty
    
    Test Data:
    - Input: "mgr002" (another manager UID)
    
    Assertions:
    - members is a list
    - List contains strings (employee IDs)
    - List is not empty
    
    How to Run:
        pytest tests/test_org.py::test_org_members_list -v
    
    Expected Result:
        test_org_members_list PASSED
    """
    # Call function
    data = get_org_members("mgr002")
    
    # Verify members is a list
    assert isinstance(data["members"], list), "members should be a list"
    
    # Verify list is not empty (manager should have at least 1 report)
    assert len(data["members"]) > 0, "Manager should have at least one direct report"
    
    # Verify all items in list are strings (employee IDs)
    for member in data["members"]:
        assert isinstance(member, str), f"Employee ID should be string, got {type(member)}"
        assert len(member) > 0, "Employee ID should not be empty"


def test_org_members_team_size():
    """
    Test get_org_members returns reasonable team size.
    
    This test validates that team sizes are realistic for typical
    organizational structures (usually 1-20 direct reports).
    
    Test Data:
    - Input: "mgr003" (manager UID)
    
    Assertions:
    - Team size is between 1 and 20 members
    - Team size is reasonable for typical org structure
    
    How to Run:
        pytest tests/test_org.py::test_org_members_team_size -v
    
    Expected Result:
        test_org_members_team_size PASSED
    """
    # Call function
    data = get_org_members("mgr003")
    
    # Get team size
    team_size = len(data["members"])
    
    # Verify team size is realistic
    # Most managers have 1-15 direct reports
    assert 1 <= team_size <= 15, \
        f"Team size {team_size} outside realistic range (1-15)"


def test_org_members_uniqueness():
    """
    Test get_org_members returns unique employee IDs.
    
    This test ensures there are no duplicate employee IDs in the list,
    which would indicate data quality issues.
    
    Test Data:
    - Input: "mgr004" (manager UID)
    
    Assertions:
    - No duplicate employee IDs in members list
    - List length equals unique set length
    
    How to Run:
        pytest tests/test_org.py::test_org_members_uniqueness -v
    
    Expected Result:
        test_org_members_uniqueness PASSED
    """
    # Call function
    data = get_org_members("mgr004")
    
    # Verify no duplicates in member list
    members = data["members"]
    unique_members = set(members)
    
    assert len(members) == len(unique_members), \
        f"Found duplicate members: {len(members)} items, {len(unique_members)} unique"


def test_org_members_consistency():
    """
    Test get_org_members returns consistent data across multiple calls.
    
    This test validates that the function returns the same data
    when called multiple times with the same input (data consistency).
    
    Test Data:
    - Input: "mgr005" (manager UID)
    
    Assertions:
    - Multiple calls return identical data
    - No random variations
    - Data is stable (not dependent on time)
    
    How to Run:
        pytest tests/test_org.py::test_org_members_consistency -v
    
    Expected Result:
        test_org_members_consistency PASSED
    """
    # Call function multiple times with same input
    data1 = get_org_members("mgr005")
    data2 = get_org_members("mgr005")
    data3 = get_org_members("mgr005")
    
    # Verify responses are identical
    assert data1 == data2, "Different results on first and second call"
    assert data2 == data3, "Different results on second and third call"
    
    # Verify manager field matches
    assert data1["manager"] == data2["manager"] == data3["manager"]
    
    # Verify members lists are identical
    assert data1["members"] == data2["members"] == data3["members"]
