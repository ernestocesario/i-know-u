import os
import sys
from pathlib import Path


class AppProperties:

    # *******************************************************
    # Private methods
    # *******************************************************

    @staticmethod
    def get_base_dir() -> str:
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return str(Path(os.path.dirname(os.path.abspath(__file__))).resolve().parent.parent)



    # *******************************************************
    # Constants methods
    # *******************************************************

    # Base directory of the application
    BASE_DIR: str = get_base_dir()

    # Directory to store application data
    DATA_DIR: str = os.path.join(BASE_DIR, "data")

    # Directory to store content files
    CONTENTS_DIR: str = os.path.join(DATA_DIR, "contents")

    # Directory to store vector data
    VECTOR_STORE_DIR = os.path.join("data", "vector_store")