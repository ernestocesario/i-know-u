from src.config.rdb import create_db_and_tables
from src.models import *


def main():
    print("Initializing the database...")
    try:
        create_db_and_tables()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing the database: {e}")


if __name__ == "__main__":
    main()