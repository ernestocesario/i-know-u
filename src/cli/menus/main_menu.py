import sys

import questionary
from questionary import Choice
from rich.align import Align
from rich.console import Group
from rich.text import Text

from src.cli.components.headers import print_header
from src.cli.context import CliContext
# Import submenus
from src.cli.menus.analysis_menu import show_analysis_menu
from src.cli.menus.manage_data_menu import show_manage_data_menu
from src.cli.styles import q_style, console


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

    description = Text(justify="center")
    description.append("AI-Powered Social Media Profile Analyzer\n\n", style="bold red")
    description.append("Leveraging LLM technology to expose hidden behavioral patterns and extract undisclosed personal information from publicly available data", style="dim italic white")

    # Separator of 2/3 console width
    separator_width = int(console.width * 2 / 3)
    separator = Text("━" * separator_width, style="dim red")

    tech_info = Text(justify="center")
    tech_info.append("🧠 Psychological Profiling\n", style="bold white")
    tech_info.append("🎯 Hidden Interest Discovery\n", style="bold white")
    tech_info.append("🕵️  Behavioral Timeline Reconstruction\n", style="bold white")
    tech_info.append("👁️  Visual Content Intelligence\n", style="bold white")
    tech_info.append("🕸️  Social Network Analysis", style="bold white")

    credits_info = Text(justify="center")
    credits_info.append("Created by ", style="dim italic")
    credits_info.append("Ernesto Cesario", style="bold cyan")
    credits_info.append("\n")
    credits_info.append("🔗 ", style="dim cyan")
    credits_info.append("github.com/ernestocesario", style="dim cyan link https://github.com/ernestocesario")
    credits_info.append("\n\n")
    credits_info.append("© 2026 - For educational purposes only", style="dim italic black on red")

    group = Group(
        Align.center(description),
        Text(""),
        Align.center(separator),
        Text(""),
        Align.center(tech_info),
        Text("\n\n"),
        Align.center(credits_info)
    )

    console.print(
            group
    )
    console.print("")