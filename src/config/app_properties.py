import os
import sys


class AppProperties:

    # *******************************************************
    # Private methods
    # *******************************************************

    @staticmethod
    def get_base_dir() -> str:
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))



    # *******************************************************
    # Constants methods
    # *******************************************************

    BASE_DIR: str = get_base_dir()
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    CONTENTS_DIR: str = os.path.join(DATA_DIR, "contents")