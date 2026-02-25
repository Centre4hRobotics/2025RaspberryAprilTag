import pytest
from unittest.mock import MagicMock
from enum import Enum
from src.settings import FilterList, ListType


def create_mock_tag(tag_id):
    tag = MagicMock()
    tag.id = tag_id
    return tag

@pytest.mark.parametrize("config, input_ids, expected_ids", [
    ({"whitelist": [1, 2], "blacklist": None}, [1, 2, 3, 33], [1, 2]),
    ({"whitelist": None, "blacklist": [1]}, [1, 2, 3, 33], [2, 3]),
    ({"whitelist": None, "blacklist": None}, [1, 5, 33], [1, 5]),
], ids=[
    "Case 1: Whitelist Mode",
    "Case 2: Blacklist Mode",
    "Case 3: Allow All Mode"
])
def test_filter_tags_logic(config, input_ids, expected_ids):
    # Setup
    filter_list = FilterList(config)
    tags = [create_mock_tag(tag_id) for tag_id in input_ids]
    
    # Execute
    results = filter_list.filter_tags(tags)
    result_ids = [tag.id for tag in results]
    
    # Assert
    assert result_ids == expected_ids

def test_filter_list_raises_error_on_both_set():
    """Ensure the code crashes if the user provides both lists."""

    config = {"whitelist": [1], "blacklist": [2]}
    with pytest.raises(ValueError, match="Whitelist and Blacklist are both set!"):
        FilterList(config)
