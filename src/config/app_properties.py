import os
import sys
from pathlib import Path
from typing import Optional

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


    @staticmethod
    def get_env_int(name: str, default: Optional[int] = None) -> Optional[int]:
        value = os.getenv(name)

        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Environment variable '{name}' must be an integer")



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



    # *******************************************************
    # Env variables
    # *******************************************************

    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "")

    K_RAG: Optional[int] = get_env_int("K_RAG")

    IMPORT_LIMIT_STORIES: Optional[int] = get_env_int("IMPORT_LIMIT_STORIES")
    IMPORT_LIMIT_POSTS: Optional[int] = get_env_int("IMPORT_LIMIT_POSTS")
    IMPORT_LIMIT_CONTENTS_PER_HIGHLIGHT: Optional[int] = get_env_int("IMPORT_LIMIT_CONTENTS_PER_HIGHLIGHT")