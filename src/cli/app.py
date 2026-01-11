import sys
import logging

from src.config.logger_setup import configure_logging

from src.cli.context import CliContext
from src.cli.styles import print_error, print_info
from src.cli.menus.main_menu import show_main_menu


def main():
    configure_logging()

    ctx = None
    try:
        print("Initializing IKU System...", end="\r")
        ctx = CliContext()

        # Launch UI
        show_main_menu(ctx)

    except KeyboardInterrupt:
        # Clean handling of Ctrl+C
        print("\n")
        print_info("Operation cancelled by user. Exiting...")
        sys.exit(0)

    except Exception as e:
        # Handling uncaught critical errors
        print_error(f"Critical Error: {e}")
        raise e

    finally:
        # Cleanup
        if ctx:
            ctx.close()
