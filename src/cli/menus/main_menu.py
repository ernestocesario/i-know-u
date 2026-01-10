import sys
import questionary
from questionary import Choice

from src.cli.context import CliContext
from src.cli.styles import q_style, print_info, console
from src.cli.components.headers import print_header

# Import submenus
from src.cli.menus.analysis_menu import show_analysis_menu
from src.cli.menus.manage_data_menu import show_manage_data_menu


def show_main_menu(ctx: CliContext):
    """
    The Top-Level Menu loop.
    """
    while True:
        print_header("MAIN MENU")

        choice = questionary.select(
            "Select an option:",
            choices=[
                Choice("Analyze Profile", value="analyze"),
                Choice("Manage Data", value="manage"),
                Choice("About", value="about"),
                questionary.Separator(),
                Choice("Exit", value="exit")
            ],
            style=q_style
        ).ask()

        if choice == "exit":
            sys.exit(0)

        elif choice == "manage":
            show_manage_data_menu(ctx)

        elif choice == "analyze":
            _handle_analyze_flow(ctx)

        elif choice == "about":
            _show_about()
            questionary.press_any_key_to_continue().ask()


def _handle_analyze_flow(ctx: CliContext):
    """
    Flow: Ask Username -> Enter Analysis Menu
    """
    print_header("PROFILE SELECTION")

    username = questionary.text(
        "Enter the target username:",
        style=q_style
    ).ask()

    if not username:
        return  # Return to main menu if empty

    # Clean input (trim, lowercase if desired)
    username = username.strip().lower()

    # Set global context for current session
    ctx.set_current_user(username)

    # Enter the analysis submenu
    show_analysis_menu(ctx)


def _show_about():
    print_header("ABOUT")
    console.print(
        "[bold cyan]IKU - I Know U/bold cyan]\n"
        "An AI-powered tool for social media analysis using RAG and Computer Vision.\n\n"
        "[dim]Powered by Google Gemma, ChromaDB, and SQLModel.[/dim]\n"
    )
