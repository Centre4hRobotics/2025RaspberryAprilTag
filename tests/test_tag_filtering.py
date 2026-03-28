""" Tests for AprilTag ID filtering logic, verifying whitelist and blacklist behaviors. """
import pytest
from unittest.mock import MagicMock
from src.settings.filter import FilterList

class TestFilterList:
    """ Groups tests for tag filtering logic, including whitelist and blacklist modes. """

    # --- Helper Method ---

    @pytest.fixture
    def mock_tag_id(self):
        """
        Creates a 'stunt double' for a Tag.
        Instead of building a real, complex Tag object, we use MagicMock
        to create a simple object that just has an 'id' number.
        """
        def _make(tag_id: int):
            tag = MagicMock()
            tag.id = tag_id
            return tag
        return _make

    # --- Multi-Scenario Testing ---

    @pytest.mark.parametrize("config, input_ids, expected_ids", [
        (
            # Scenario 1: Whitelist Mode
            {"whitelist": list(range(1, 11)), "blacklist": None},
            list(range(1, 33)),
            list(range(1, 11))
        ),
        (
            # Scenario 2: Blacklist Mode
            {"whitelist": None, "blacklist": list(range(1, 23))},
            list(range(1, 33)),
            list(range(23, 33))
        ),
        (
            # Scenario 3: Open Gate Mode
            {"whitelist": None, "blacklist": None},
            list(range(23, 33)),
            list(range(23, 33))
        ),
        (
            # Scenario 4: Specific Pick-and-Choose
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
    def test_filter_tags_logic(self, mock_tag_id, config, input_ids, expected_ids):
        """
        This test follows the 'Arrange, Act, Assert' pattern:
        1. Set up the data. 2. Run the logic. 3. Check if the result is correct.
        """
        # 1. Arrange: Initialize the filter and create our fake 'tags'
        filter_list = FilterList(config)
        tags = [mock_tag_id(tag_id) for tag_id in input_ids]

        # 2. Act: Run the list of tags through the filter logic
        results = filter_list.filter_tags(tags)
        result_ids = [tag.id for tag in results]

        # 3. Assert: Check if the IDs that made it through match what we expected
        assert result_ids == expected_ids

    # --- Error Handling Test ---

    def test_filter_list_raises_error_on_both_set(self):
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
