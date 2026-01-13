# Test for leave balance HR function
from app.hr_functions.leave import get_leave_balance

def test_leave_balance():
    """Test that get_leave_balance returns correct data structure"""
    data = get_leave_balance("emp1")
    assert data["annual_leave"] == 12
    assert data["sick_leave"] == 6
    assert data["casual_leave"] == 4




# - Run these commands in your terminal to add Homebrew to your PATH:
#     echo >> /Users/vivek/.zprofile
#     echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> /Users/vivek/.zprofile
#     eval "$(/opt/homebrew/bin/brew shellenv zsh)"