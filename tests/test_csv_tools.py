import pytest
from utils.csv_tools import rows

def test_rows_function_fails_given_no_file():
    """Tests the rows function fails in a certain way, given no file"""

    with pytest.raises(FileNotFoundError):
        rows_result = rows("")
