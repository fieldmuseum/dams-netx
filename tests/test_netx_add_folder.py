# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import netx_add_folder
from hypothesis import given, strategies as st


@given(row=st.builds(dict), folder_id_list=st.builds(dict), live_or_test=st.text())
def test_fuzz_add_to_folder(row: dict, folder_id_list: dict, live_or_test: str) -> None:
    netx_add_folder.add_to_folder(
        row=row, folder_id_list=folder_id_list, live_or_test=live_or_test
    )


@given(path_add_rows=st.builds(list), live_or_test=st.text())
def test_fuzz_get_unique_folder_id_list(path_add_rows: list, live_or_test: str) -> None:
    netx_add_folder.get_unique_folder_id_list(
        path_add_rows=path_add_rows, live_or_test=live_or_test
    )

