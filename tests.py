import subprocess

from logic import get_num


class Tests:
    def test_get_number(self):
        assert get_num().isnumeric(), "Expecting get_num to return a number"