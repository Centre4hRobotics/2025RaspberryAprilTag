import pytest
from unittest.mock import MagicMock
from src.settings.filter import FilterList

# --- Helper Function ---

def create_mock_tag(tag_id):
    """ 
    Creates a 'stunt double' for a Tag. 
    Instead of building a real, complex Tag object, we use MagicMock 
    to create a simple object that just has an 'id' number.
    """
    tag = MagicMock()
    tag.id = tag_id
    return tag

# --- Multi-Scenario Testing ---

# @pytest.mark.parametrize acts like a 'test factory'. 
# It runs the function below 4 different times, plugging in the 'config', 
# 'input_ids', and 'expected_ids' for each scenario.
@pytest.mark.parametrize("config, input_ids, expected_ids", [
    (
        # Scenario 1: Whitelist Mode
        # Only allow specific IDs (1 through 10) to pass through.
        {"whitelist": list(range(1, 11)), "blacklist": None}, 
        list(range(1, 33)), 
        list(range(1, 11))
    ),
    (
        # Scenario 2: Blacklist Mode
        # Block IDs 1 through 22, leaving only 23 through 32.
        {"whitelist": None, "blacklist": list(range(1, 23))}, 
        list(range(1, 33)), 
        list(range(23, 33))
    ),
    (
        # Scenario 3: Open Gate Mode
        # If no lists are provided, everything should be allowed to pass.
        {"whitelist": None, "blacklist": None}, 
        list(range(23, 33)), 
        list(range(23, 33))
    ),
    (
        # Scenario 4: Specific Pick-and-Choose
        # Test if the filter can grab 10 specific IDs scattered across a range.
        {"whitelist": [2, 5, 8, 12, 15, 19, 22, 26, 29, 32], "blacklist": None},
        list(range(1, 33)),
        [2, 5, 8, 12, 15, 19, 22, 26, 29, 32]
    ),
], ids=[
    "Whitelist (Keep 1-10)",
    "Blacklist (Exclude 1-22)",
    "Allow All (No filters)",
    "Sparse Selection (Specific IDs)"
])
def test_filter_tags_logic(config, input_ids, expected_ids):
    """
    This test follows the 'Arrange, Act, Assert' pattern:
    1. Set up the data. 2. Run the logic. 3. Check if the result is correct.
    """
    # 1. Arrange: Initialize the filter and create our fake 'tags'
    filter_list = FilterList(config)
    tags = [create_mock_tag(tag_id) for tag_id in input_ids]
    
    # 2. Act: Run the list of tags through the filter logic
    results = filter_list.filter_tags(tags)
    result_ids = [tag.id for tag in results]
    
    # 3. Assert: Check if the IDs that made it through match what we expected
    assert result_ids == expected_ids

# --- Error Handling Test ---

def test_filter_list_raises_error_on_both_set():
    """
    Tests what happens when a user gives 'illegal' instructions.
    The system shouldn't allow someone to use a Whitelist AND a Blacklist at the same time.
    """
    # Setup a configuration that breaks the rules
    config = {"whitelist": [1], "blacklist": [2]}
    
    # 'pytest.raises' is a safety net. The test will only PASS if the code 
    # correctly catches the mistake and triggers a "ValueError" message.
    with pytest.raises(ValueError, match="Whitelist and Blacklist are both set!"):
        FilterList(config)
