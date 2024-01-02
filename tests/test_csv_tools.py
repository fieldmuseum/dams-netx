import pytest
from hypothesis import given, strategies as st
from string import printable
import utils.csv_tools
import os

def test_rows_function_fails_given_no_file():
    """Tests the rows function fails in a certain way, given no file"""

    with pytest.raises(FileNotFoundError):
        utils.csv_tools.rows("")


# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

def test_fuzz_rows(file="data/csv_good_examples/pathAdd_20220811_test.csv"):
    '''Tests that a list of dictionaries is returned'''
    rows = utils.csv_tools.rows(file=file)
    assert isinstance(rows, list)
    assert isinstance(rows[0], dict)


@given(
    # input_records=st.builds(list, dict),
    # field_names=st.builds(list),
    # output_csv_file_name=st.text(alphabet=printable[0:62], 
    #                              min_size=1,  # type: int
    #                              max_size=200)
    output_csv_file_name=st.from_regex(r'[a-zA-Z0-9]', fullmatch=True)
)
def test_fuzz_write_list_of_dict_to_csv(
    # input_records: list, 
    # field_names: list, 
    output_csv_file_name: str
) -> None:
    '''Tests output runs'''
    '''(currently only tests a range of output filenames)'''
    input_records = [{'a':1,'b':2},{'a':3,'b':4}]
    field_names = list(input_records[0].keys())
    output_csv_file_name = f'testing/test_data_out/{output_csv_file_name}.csv'
    utils.csv_tools.write_list_of_dict_to_csv(
        input_records=input_records,
        field_names=field_names,
        output_csv_file_name=output_csv_file_name
    )

# def cleanup() -> None:
#     os.remove(path=output_csv_file_name)

