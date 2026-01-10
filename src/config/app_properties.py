import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

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
    # Constants
    # *******************************************************

    # App name
    APP_NAME: str = "I Know U"

    # Base directory of the application
    BASE_DIR: str = get_base_dir()

    # Log directory of the application
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")

    # Log file path
    LOG_FILE_NAME: str = "app.log"

    # Directory to store application data
    DATA_DIR: str = os.path.join(BASE_DIR, "data")

    # Directory to store content files
    CONTENTS_DIR: str = os.path.join(DATA_DIR, "contents")

    # Directory to store vector data
    VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")

    # API Keys
    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")