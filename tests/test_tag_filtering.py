import pytest
from unittest.mock import MagicMock
from src.settings import FilterList

# Helper function to simulate a Tag object. 
# MagicMock allows us to create an object that 'acts' like a real Tag 
# without needing the actual database or class logic.
def create_mock_tag(tag_id):
    tag = MagicMock()
    tag.id = tag_id
    return tag

# @pytest.mark.parametrize is a 'test multiplier'. 
# It runs the same test function multiple times using the data provided below.
# The string "config, input_ids, expected_ids" tells pytest which arguments to 
# inject into the function.
@pytest.mark.parametrize("config, input_ids, expected_ids", [
    (
        # Case 1: Whitelist (Keep only 1-10 out of 1-20)
        {"whitelist": list(range(1, 11)), "blacklist": None}, 
        list(range(1, 21)), 
        list(range(1, 11))
    ),
    (
        # Case 2: Blacklist (Exclude 1-10 out of 1-25)
        {"whitelist": None, "blacklist": list(range(1, 11))}, 
        list(range(1, 26)), 
        list(range(11, 26))
    ),
    (
        # Case 3: Allow All (Large set of 50 items)
        {"whitelist": None, "blacklist": None}, 
        list(range(100, 151)), 
        list(range(100, 151))
    ),
    (
        # Case 4: Sparse Whitelist (Only specific IDs in a large range)
        {"whitelist": [10, 20, 30, 40, 50], "blacklist": None},
        list(range(1, 101)),
        [10, 20, 30, 40, 50]
    ),
], ids=[
    # The 'ids' parameter gives each test run a readable name in the terminal output.
    "Whitelist Mode (10/20)",
    "Blacklist Mode (15/25)",
    "Allow All Mode (50 items)",
    "Sparse Whitelist (Stress Test)"
])
def test_filter_tags_logic(config, input_ids, expected_ids):
    """
    Standard test flow: Arrange -> Act -> Assert.
    This function runs 4 times with the different data sets defined above.
    """
    # 1. Arrange: Prepare the objects and state
    filter_list = FilterList(config)
    tags = [create_mock_tag(tag_id) for tag_id in input_ids]
    
    # 2. Act: Trigger the behavior we are testing
    results = filter_list.filter_tags(tags)
    result_ids = [tag.id for tag in results]
    
    # 3. Assert: Verify the outcome matches our expectations
    assert result_ids == expected_ids

def test_filter_list_raises_error_on_both_set():
    """
    Tests for 'Happy Paths' are good, but we also test for 'Sad Paths' (Expected Failures).
    This ensures the code fails safely when misused.
    """
    config = {"whitelist": [1], "blacklist": [2]}
    
    # pytest.raises acts as a 'trap'. If the code inside the 'with' block 
    # throws a ValueError, the test passes. If it doesn't throw, the test fails.
    with pytest.raises(ValueError, match="Whitelist and Blacklist are both set!"):
        FilterList(config)
